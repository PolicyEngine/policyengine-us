from policyengine_us.model_api import *


class is_born_outside_us(Variable):
    value_type = bool
    entity = Person
    label = "Was born outside the United States"
    definition_period = YEAR
    documentation = "Whether the person was born outside the United States"
