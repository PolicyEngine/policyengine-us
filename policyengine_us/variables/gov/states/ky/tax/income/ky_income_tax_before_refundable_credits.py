from policyengine_us.model_api import *


class ky_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, paramters):
        tax_before_non_refundable = tax_unit(
            "ky_income_tax_before_non_refundable_credits_unit", period
        )
        non_refundable_credits = tax_unit("ky_non_refundable_credits", period)
        return max_(tax_before_non_refundable - non_refundable_credits, 0)
