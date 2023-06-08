from policyengine_us.model_api import *


class md_tanf_is_child(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Wether is a child for MD TANF based on age, education, etc."
    documentation = "0307 Age rev 11.22.doc"

    def formula(person, period, parameters):
        person = spm_unit.members
        # younger than age 18
        child_0_17 = person("is_child", period)
        # Younger than age 19 and A full time k12 student
        younger_than_19 = person("age", period) <= 19
        k12 = person("is_in_k12_school", period)
        k12_younger_than_19 = k12 & younger_than_19
        # age 19 and a full time student
        full_time_student = person("is_full_time_college_student", period)
        school_enrolled_19_year_old = full_time_student & younger_than_19
        # return
        return child_0_17 | school_enrolled_19_year_old | k12_younger_than_19
