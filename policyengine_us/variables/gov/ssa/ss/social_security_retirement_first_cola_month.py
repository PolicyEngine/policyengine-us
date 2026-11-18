from policyengine_us.model_api import *


class social_security_retirement_first_cola_month(Variable):
    value_type = int
    default_value = 1
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement first cola month"
    documentation = "First exposed COLA payment month (1 through 12)."
