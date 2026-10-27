from policyengine_us.model_api import *


class social_security_retirement_cola_withheld(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement cola withheld"
    documentation = "Whether this payment year COLA is withheld; inactive unless withholding_enabled is set."
