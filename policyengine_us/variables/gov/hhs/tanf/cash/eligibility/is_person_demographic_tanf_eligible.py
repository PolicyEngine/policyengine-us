from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Person demographic eligibility for TANF"
    documentation = "Whether this person meets the demographic requirements for TANF eligibility"

    def formula(person, period, parameters):
        # Federal age limits for TANF eligibility
        # Get age for the year, not the month
        age = person("age", period.this_year)
        is_pregnant = person("is_pregnant", period)
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        # A person is eligible if they are under the age limit
        # Different age limits for students vs non-students
        # For TANF, "student" means secondary school student per 45 CFR § 260.30
        is_student = person("is_in_secondary_school", period)
        age_limit = where(is_student, p.student, p.non_student)
        age_eligible = age < age_limit

        # Also eligible if pregnant
        return age_eligible | is_pregnant
