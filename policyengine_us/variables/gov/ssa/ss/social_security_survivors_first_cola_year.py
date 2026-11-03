from policyengine_us.model_api import *


class social_security_survivors_first_cola_year(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors first cola year"
    documentation = "First exposed COLA payment year; zero requests the documented population proxy."
