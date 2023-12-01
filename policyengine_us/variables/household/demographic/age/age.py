from policyengine_us.model_api import *


class age(Variable):
    value_type = float
    entity = Person
    label = "age"
    definition_period = YEAR
    default_value = 40
