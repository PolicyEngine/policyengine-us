from policyengine_us.model_api import *


class ca_state_disability_insurance(Variable):
    value_type = float
    entity = Person
    label = "California state disability insurance (SDI)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
