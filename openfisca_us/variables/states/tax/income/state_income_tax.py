from openfisca_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax"
    unit = USD
    documentation = "State income tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        pit = parameters(period).states.tax.income
        state = tax_unit.household("state_code_str", period)
        rate = pit.rates[state]
        return tax_unit("state_taxable_income", period) * rate
