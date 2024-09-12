from policyengine_us.model_api import *


class is_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Is veteran"
    definition_period = YEAR
