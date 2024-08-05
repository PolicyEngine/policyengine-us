from policyengine_us.model_api import *


class out_of_state_purchase(Variable):
    value_type = float
    entity = TaxUnit
    label = "Out of state purchase"
    unit = USD
    definition_period = YEAR