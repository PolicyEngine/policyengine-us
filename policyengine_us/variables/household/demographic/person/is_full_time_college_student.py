from policyengine_us.model_api import *


class is_full_time_college_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a full time college student"
    definition_period = YEAR
