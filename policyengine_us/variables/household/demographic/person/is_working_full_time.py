from policyengine_us.model_api import *


class is_working_full_time(Variable):
    value_type = bool
    entity = Person
    label = "Is working full time"
    definition_period = YEAR
