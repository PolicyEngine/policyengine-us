from policyengine_us.model_api import *


class is_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a part or full time student"
    definition_period = YEAR

    def formula(person, period, parameters):
        is_full_time_student = person("is_full_time_student", period)
        is_part_time_student = person("is_part_time_student", period)
        return is_full_time_student | is_part_time_student
