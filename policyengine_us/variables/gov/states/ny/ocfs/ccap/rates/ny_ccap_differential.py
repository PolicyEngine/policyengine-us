from policyengine_us.model_api import *


class ny_ccap_differential(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP combined payment differential"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "Adds the child's nontraditional-hours, homelessness and eligible "
        "provider accreditation differentials, subject to the combined limit. "
        "From April 1, 2025, Social Services Law 410-x(10) raises the "
        "nontraditional-hours and licensed or registered homelessness minimum "
        "from 5% to 10%; an elected accreditation differential keeps its 5% "
        "minimum. The default limit assumes no OCFS waiver. Confirmed district "
        "rates replace state defaults."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        # PDF pages 9-10
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
        "https://www.nysenate.gov/legislation/laws/SOS/410-X",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.differentials
        provider = person("childcare_provider_type_group", period.this_year)
        providers = provider.possible_values
        licensed = (provider == providers.DCC_SACC) | (provider == providers.FDC_GFDC)
        county = person.household("county_str", period.this_year)
        group = person.household("ny_ccap_county_group", period.this_year)
        nyc = group == group.possible_values.GROUP_4
        monroe = county == "MONROE_COUNTY_NY"
        nontraditional_rate = where(
            nyc, p.nyc_nontraditional_hours, p.nontraditional_hours
        )
        accreditation_rate = where(monroe, p.monroe_accreditation, p.accreditation)
        exempt_homelessness_rate = where(
            monroe, p.monroe_legally_exempt_homelessness, p.legally_exempt_homelessness
        )
        # Optional accreditation pays zero until a district adopts it, then
        # its own minimum and the shared individual maximum apply.
        accreditation_rate = where(
            accreditation_rate > 0,
            min_(
                max_(accreditation_rate, p.accreditation_minimum),
                p.maximum_individual,
            ),
            0,
        )
        homelessness_rate = where(
            licensed,
            min_(max_(p.homelessness, p.minimum), p.maximum_individual),
            min_(max_(exempt_homelessness_rate, 0), p.maximum_individual),
        )
        nontraditional_rate = min_(
            max_(nontraditional_rate, p.minimum), p.maximum_individual
        )
        nontraditional = person("ny_ccap_nontraditional_hours", period.this_year)
        homeless = person.household("is_homeless", period.this_year)
        accredited = person("ny_ccap_accredited_provider", period.this_year)
        combined = (
            nontraditional * nontraditional_rate
            + homeless * homelessness_rate
            + accredited * licensed * accreditation_rate
        )
        return min_(combined, p.maximum)
