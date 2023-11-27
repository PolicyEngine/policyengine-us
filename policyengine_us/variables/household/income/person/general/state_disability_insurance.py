from policyengine_us.model_api import *


class state_disability_insurance(Variable):
    value_type = float
    entity = Person
    label = "State diability insurance (SDI)"
    unit = USD
    definition_period = YEAR
