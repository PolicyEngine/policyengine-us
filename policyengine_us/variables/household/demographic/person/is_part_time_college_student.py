from policyengine_us.model_api import *


class is_part_time_college_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a part-time college student"
    documentation = "Enrolled at least half-time but less than full-time in an institution of higher education"
    definition_period = YEAR
