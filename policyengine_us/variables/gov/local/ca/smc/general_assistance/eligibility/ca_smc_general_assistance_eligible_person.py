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
        # income at the moment. The SSI gate below captures SSI recipients
        # but does not separately exclude CAPI recipients.
        p = parameters(period).gov.local.ca.smc.general_assistance
        adult = person("age", period.this_year) >= p.minimum_age
        immigration_eligible = person(
            "ca_smc_general_assistance_immigration_status_eligible_person",
            period,
        )
        not_on_ssi = person("ssi", period) == 0
        meets_work_requirements = person(
            "ca_smc_general_assistance_meets_work_requirements", period
        )
        return adult & immigration_eligible & not_on_ssi & meets_work_requirements
