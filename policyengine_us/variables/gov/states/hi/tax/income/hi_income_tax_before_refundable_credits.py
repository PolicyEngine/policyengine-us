from policyengine_us.model_api import *


class hi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # Since Hawaii model does not have non_refundable_credits
        # only return refundable credits
        return tax_unit("hi_income_tax_before_credits", period)
