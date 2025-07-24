from policyengine_us.model_api import *


class metered_gas_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Metered gas expense"
    unit = USD
    definition_period = YEAR
