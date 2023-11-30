from policyengine_us.model_api import *


class mt_income_tax_after_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax after non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        before_refundable_credits = tax_unit(
            "mt_income_tax_before_refundable_credits", period
        )
        non_refundable_credits = tax_unit("mt_non_refundable_credits", period)
        return max_(before_refundable_credits - non_refundable_credits, 0)
