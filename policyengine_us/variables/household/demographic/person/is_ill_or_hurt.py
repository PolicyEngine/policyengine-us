from policyengine_us.model_api import *


class is_ill_or_hurt(Variable):
    value_type = bool
    entity = Person
    label = "Is ill or hurt (must be confirmed by a doctor)"
    definition_period = YEAR
