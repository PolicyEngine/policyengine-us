from policyengine_us.model_api import *


class is_self_employed(Variable):
    value_type = bool
    entity = Person
    label = "Is self-employed"
    definition_period = YEAR
