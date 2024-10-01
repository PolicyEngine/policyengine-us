from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."
    reference = "https://www.law.cornell.edu/cfr/text/45/260.30"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.tanf.cash.eligibility
        age = person("age", period)
        below_age_threshold = age < p.age_threshold
        below_age_limit = age < p.age_limit
        secondary_school_student = person("is_in_secondary_school", period)
        secondary_school_below_age_limit_student = (
            secondary_school_student & below_age_limit
        )
        pregnant = person("is_pregnant", period)
        return (
            below_age_threshold
            | secondary_school_below_age_limit_student
            | pregnant
        )
