from openfisca_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax"
    unit = USD
    definition_period = YEAR

    def formula_2021(tax_unit, period, parameters):
        return tax_unit("ma_income_tax", period)
