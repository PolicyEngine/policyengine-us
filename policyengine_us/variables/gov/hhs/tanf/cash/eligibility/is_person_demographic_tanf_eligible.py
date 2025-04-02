from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."
    reference = "https://www.law.cornell.edu/cfr/text/45/260.30"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        age = person("monthly_age", period)
        age_eligible_if_student = age < p.student
        age_eligible_non_student = age < p.non_student
        secondary_school_student = person("is_in_secondary_school", period)
        age_eligible_secondary_school_student = (
            secondary_school_student & age_eligible_if_student
        )
        pregnant = person("is_pregnant", period)
        return (
            age_eligible_non_student
            | age_eligible_secondary_school_student
            | pregnant
        )
