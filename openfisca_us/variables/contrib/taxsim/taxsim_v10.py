from openfisca_us.model_api import *


class taxsim_v10(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal AGI"
    unit = USD
    documentation = "TAXSIM federal AGI"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("adjusted_gross_income", period)
