from policyengine_us.model_api import *


class nm_ssi_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "New Mexico SSI state supplement eligible"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        "https://srca.nm.gov/parts/title08/08.106.0500.html",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/nm.html",
    )

    def formula(person, period, parameters):
        ssi_eligible = person("is_ssi_eligible_individual", period)
        age = person("age", period)
        p = parameters(period).gov.states.nm.hca.ssi_supplement
        meets_age = age >= p.min_age
        in_residential_care = person("is_in_adult_residential_care", period)
        return ssi_eligible & meets_age & in_residential_care
