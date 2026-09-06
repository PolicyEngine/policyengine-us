from policyengine_us.model_api import *


class metered_gas_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Metered gas expense"
    unit = USD
    definition_period = YEAR
    documentation = "Deprecated: a duplicate of gas_expense, which every program now reads (the Illinois AABD metered gas allowance included). Set gas_expense instead; this input is no longer read anywhere."
