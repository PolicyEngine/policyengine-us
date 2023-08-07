from policyengine_us.model_api import *


class is_grandparent(Variable):
    value_type = bool
    entity = Person
    label = "Is a grandparent"
    definition_period = YEAR
