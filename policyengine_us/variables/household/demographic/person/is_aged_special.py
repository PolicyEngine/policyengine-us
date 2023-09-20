from policyengine_us.model_api import *


class is_aged_special(Variable):
    value_type = bool
    entity = Person
    label = "Is an aged over 65 not claiming a retirement income exemption"
    definition_period = YEAR
