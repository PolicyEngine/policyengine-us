from policyengine_us.model_api import *


class dwks6(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS6"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        dwks2 = add(tax_unit, period, ["qualified_dividend_income"])
        dwks3 = tax_unit("investment_income_form_4952", period)
        # dwks4 always assumed to be zero
        dwks5 = max_(0, dwks3)
        return max_(0, dwks2 - dwks5)
