from policyengine_us.model_api import *


class ct_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        tax_before_non_refundable_credits = tax_unit(
            "ct_income_tax_after_amt", period
        )
        non_refundable_credits = tax_unit("ct_non_refundable_credits", period)
        return max_(
            tax_before_non_refundable_credits - non_refundable_credits, 0
        )
