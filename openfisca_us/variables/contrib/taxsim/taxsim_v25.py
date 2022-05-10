from openfisca_us.model_api import *


class taxsim_v25(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("eitc", period)
