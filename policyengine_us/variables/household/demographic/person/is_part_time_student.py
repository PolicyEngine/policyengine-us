from policyengine_us.model_api import *


class is_part_time_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a part time student"
    definition_period = YEAR
