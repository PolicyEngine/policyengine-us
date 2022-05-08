from openfisca_us.model_api import *


class taxsim_intrec(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable interest"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["taxable_interest_income"])
