from policyengine_us.model_api import *


class hi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("hi_income_tax_before_non_refundable_credits", period)
        # Nonrefundable credits are already limited to the tax left after
        # refundable credits (Form N-11, line 34), so subtracting refundable
        # credits from this amount gives the balance on line 36.
        non_refundable_credits = tax_unit("hi_non_refundable_credits", period)
        return max_(income_tax - non_refundable_credits, 0)
