from policyengine_us.model_api import *


class ga_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        tax_before_refundable_credits = tax_unit(
            "ga_income_tax_before_non_refundable_credits", period
        )
        credits = tax_unit("ga_non_refundable_credits", period)
        return max_(0, tax_before_refundable_credits - credits)
