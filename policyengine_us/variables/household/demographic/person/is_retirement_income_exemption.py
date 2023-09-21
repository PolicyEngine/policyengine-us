from policyengine_us.model_api import *


class is_retirement_income_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Is an aged over 65 claiming a retirement income exemption"
    definition_period = YEAR
