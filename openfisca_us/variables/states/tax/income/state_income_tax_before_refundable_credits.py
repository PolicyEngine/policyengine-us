from openfisca_us.model_api import *


class state_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax before refundable credits"
    unit = USD
    documentation = "State income tax before refundable credits"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        pit = parameters(period).states.tax.income
        state = tax_unit.household("state_code_str", period)
        rate = pit.rates[state]
        exempt = tax_unit("is_state_income_tax_exempt", period)
        return tax_unit("state_taxable_income", period) * rate * ~exempt
