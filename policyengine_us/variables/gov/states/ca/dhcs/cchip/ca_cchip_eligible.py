from policyengine_us.model_api import *


class ca_cchip_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the California County Children's Health Initiative Program"
    definition_period = YEAR
    reference = (
        "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/SPA-24-0012-Approval.pdf#page=12",
        "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/SPA-24-0012-Approval.pdf#page=23",
        "https://stgenssa.sccgov.org/debs/program_handbooks/medi-cal/assets/35StCtyAdminHealthIns/CCHIP.htm",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho-12-002.pdf#page=1",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.dhcs.cchip
        county = person.household("county_str", period)
        in_cchip_county = np.isin(county, p.counties)
        # The state plan covers children "from age 0 up to age 19", the federal
        # CHIP definition of a child.
        age = person("age", period)
        age_eligible = age < parameters(period).gov.hhs.chip.child.max_age
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        # CMS SHO #12-002 excludes DACA from the CHIP lawfully residing option.
        daca = istatus == istatus.possible_values.DACA
        immigration_eligible = ~(undocumented | daca)
        # NOTE: The 266 percent FPL lower bound of the CCHIP band is the Medi-Cal
        # child limit; counties refer every Medi-Cal eligible child there.
        medicaid_eligible = person("is_medicaid_eligible", period)
        income_eligible = person("medicaid_income_level", period) <= p.income_limit
        has_disqualifying_coverage = person(
            "has_chip_disqualifying_health_coverage", period
        )
        # The county handbook also excludes children with employer coverage
        # available, with no affordability test; the ACA affordable offer input
        # is the closest available proxy.
        offered_esi = person("offered_aca_disqualifying_esi", period)
        return (
            in_cchip_county
            & age_eligible
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
            & ~has_disqualifying_coverage
            & ~offered_esi
        )
