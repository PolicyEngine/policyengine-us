from openfisca_us.model_api import *


class taxsim_siitax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax liability"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("state_income_tax", period)
