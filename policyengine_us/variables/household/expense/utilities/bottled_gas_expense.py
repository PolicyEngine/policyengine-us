from policyengine_us.model_api import *


class bottled_gas_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Bottled gas expense"
    unit = USD
    definition_period = YEAR
