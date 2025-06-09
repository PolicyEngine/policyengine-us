from policyengine_us.model_api import *


class is_working_part_time(Variable):
    value_type = bool
    entity = Person
    label = "Is working part time"
    definition_period = YEAR
