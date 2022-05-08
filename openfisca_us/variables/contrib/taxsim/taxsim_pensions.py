from openfisca_us.model_api import *


class taxsim_pensions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pensions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["pension_income"])
