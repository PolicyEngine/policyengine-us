from policyengine_us.model_api import *


class ca_smc_general_assistance_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for San Mateo County General Assistance"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/hsa/general-assistance-ga",
        "https://sanmateocounty.legistar.com/View.ashx?GUID=25359405-C9EB-4566-AE97-D927CC455B02&ID=9802358&M=F#page=2",
    )

    def formula(person, period, parameters):
        # We don't track 15-day county residency, fleeing-felon
        # disqualification, or the requirement to apply for other potential
        # income at the moment. SSI and CAPI recipients are excluded because
        # GA is interim aid pending those categorical benefits (Board File
        # 26-290; SSP-14 IAR framing).
        # The work requirement does not gate eligibility: an initial applicant
        # only needs to be employable or willing to seek and accept work, which
        # we don't track at the moment, so it is assumed met.
        p = parameters(period).gov.local.ca.smc.general_assistance
        adult = person("age", period.this_year) >= p.minimum_age
        immigration_eligible = person(
            "ca_smc_general_assistance_immigration_status_eligible_person",
            period,
        )
        not_on_ssi = (person("ssi", period) == 0) & ~person("receives_ssi", period)
        not_capi_eligible = ~person("ca_capi_eligible_person", period.this_year)
        return adult & immigration_eligible & not_on_ssi & not_capi_eligible
