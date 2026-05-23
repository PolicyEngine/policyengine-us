from policyengine_us.model_api import *


class ak_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Alaska Adult Public Assistance eligible"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=1",
        "https://www.akleg.gov/basis/statutes.asp#47.25.430",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ssp.eligibility
        return (
            person("is_ssi_eligible", period)
            & (person("age", period.this_year) >= p.age_threshold)
            & ~person.household("ak_ssp_excluded_institutional_setting", period)
        )
