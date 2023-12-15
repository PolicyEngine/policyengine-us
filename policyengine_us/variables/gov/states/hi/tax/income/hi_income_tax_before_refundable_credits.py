from policyengine_us.model_api import *


class hi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    # Old: "return max_(hi_income_tax_before_credits - non_refundable_credits, 0)"
    # Since Hawaii model does not have non_refundable_credits
    # only return hi_income_tax_before_credits
    adds = ["hi_income_tax_before_credits"]
