from openfisca_us.model_api import *


class taxsim_v12(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social Security in AGI"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("tax_unit_taxable_social_security", period)
