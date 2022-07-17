from openfisca_us.model_api import *


class income_tax_capped_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable tax credits"
    unit = USD
    documentation = "Capped value of non-refundable tax credits"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("income_tax_before_credits", period),
            tax_unit("income_tax_non_refundable_credits", period),
        )
