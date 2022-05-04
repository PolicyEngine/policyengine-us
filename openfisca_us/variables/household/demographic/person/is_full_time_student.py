from openfisca_us.model_api import *


class is_full_time_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a full time student"
    definition_period = YEAR

    def formula(person, period, parameters):
        in_college = person("is_full_time_college_student", period)
        in_k12 = person("is_in_k12_school", period)
        return in_college | in_k12
