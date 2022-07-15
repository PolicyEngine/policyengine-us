from openfisca_us.model_api import *

class il_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        exemption_allowance = tax_unit("il_exemption_allowance", period)
        base_income = tax_unit("il_base_income", period)
        rate = parameters(period).gov.states.il.tax.income.rate

        return max(base_income - exemption_allowance, 0) * rate