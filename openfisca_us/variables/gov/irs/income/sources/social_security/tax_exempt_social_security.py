from openfisca_us.model_api import *


class tax_exempt_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax-exempt Social Security"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        total_ss = tax_unit("tax_unit_social_security", period)
        taxable_ss = tax_unit("tax_unit_taxable_social_security", period)
        return total_ss - taxable_ss
