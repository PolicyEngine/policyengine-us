from policyengine_us.model_api import *


class is_enrolled_in_head_start(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in a Head Start or Early Head Start program"
    definition_period = YEAR
