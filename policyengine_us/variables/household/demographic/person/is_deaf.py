from policyengine_us.model_api import *


class is_deaf(Variable):
    value_type = bool
    entity = Person
    label = "Is deaf"
    definition_period = YEAR
