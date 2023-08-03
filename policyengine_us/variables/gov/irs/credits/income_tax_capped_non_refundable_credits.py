from policyengine_us.model_api import *


class income_tax_capped_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "non-refundable tax credits"
    unit = USD
    documentation = "Capped value of non-refundable tax credits"
    definition_period = YEAR
    adds = ["income_tax_non_refundable_credits"]
    subtracts = ["income_tax_unavailable_non_refundable_credits"]


class income_tax_unavailable_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "unavailable non-refundable tax credits"
    unit = USD
    documentation = "Total value of non-refundable tax credits that were not available to the filer due to having too low income tax."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return -min_(
            tax_unit("income_tax_before_credits", period),
            tax_unit("income_tax_non_refundable_credits", period),
        ) + tax_unit("income_tax_non_refundable_credits", period)
