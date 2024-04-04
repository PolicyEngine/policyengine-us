from policyengine_us.model_api import *


class az_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Arizona Cash Assistance"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        # Get the age of the person
        age = person("age", period)
        # Determine whether they are a student
        student = person("is_full_time_student", period)
        # Determine the age thresholds
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.age_threshold
        age_threshold = where(student, p.student, p.non_student)
        return age < age_threshold
