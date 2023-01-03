from policyengine_us.model_api import *


class positive_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Positive AGI"
    unit = USD
    documentation = "Negative AGI values capped at zero"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(tax_unit("adjusted_gross_income", period), 0)
