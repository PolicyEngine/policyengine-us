from policyengine_us.model_api import *


class has_developmental_delay(Variable):
    value_type = bool
    entity = Person
    label = "Has a developmental delay"
    definition_period = YEAR
    documentation = "Whether the child has a screening-indicated developmental delay or disability"
