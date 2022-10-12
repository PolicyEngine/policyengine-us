from policyengine_us.model_api import *


class amt_non_agi_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income considered for AMT but not AGI"
    unit = USD
    definition_period = YEAR
