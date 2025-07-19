from policyengine_us.model_api import *


class natural_gas_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Natural gas expense"
    unit = USD
    definition_period = YEAR
