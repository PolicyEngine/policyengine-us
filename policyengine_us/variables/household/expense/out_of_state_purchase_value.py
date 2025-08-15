from policyengine_us.model_api import *


class out_of_state_purchase_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Values of goods purchased out of state"
    unit = USD
    definition_period = YEAR
