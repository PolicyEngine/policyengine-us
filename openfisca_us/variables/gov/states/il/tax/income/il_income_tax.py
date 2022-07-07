from openfisca_us.model_api import *


class il_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        il_agi = tax_unit("il_add_backs", period)
        rate = parameters(period).gov.states.il.tax.income.rate

        return il_agi * rate
