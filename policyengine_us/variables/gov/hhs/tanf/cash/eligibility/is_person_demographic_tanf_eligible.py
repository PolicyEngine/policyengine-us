from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."
    reference = "https://www.law.cornell.edu/cfr/text/45/260.30"

    def formula(person, period, parameters):
        age_limit = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        age = person("age", period)
        below_age_limit = age < age_limit
        at_age_limit = age == age_limit
        secondary_school_student = person("is_in_secondary_school", period)
        secondary_school_at_age_limit_student = (
            secondary_school_student & at_age_limit
        )
        pregnant = person("is_pregnant", period)
        return (
            below_age_limit | secondary_school_at_age_limit_student | pregnant
        )
