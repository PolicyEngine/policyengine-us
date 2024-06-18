from policyengine_us.model_api import *


class is_deceased(Variable):
    value_type = bool
    entity = Person
    label = "Is deceased"
    definition_period = YEAR
