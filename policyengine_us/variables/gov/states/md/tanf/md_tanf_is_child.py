from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is a child in Maryland"
    documentation = "0307 Age rev 11.22"

    def formula(person, period, parameters):
        child_0_17 = person("is_child", period)
        full_time_k12_student = person("is_in_k12_school", period)
        k12_school_enrolled_19_year_old = full_time_k12_student & (
            person("age", period) <= 19
        )
        return child_0_17 | k12_school_enrolled_19_year_old
