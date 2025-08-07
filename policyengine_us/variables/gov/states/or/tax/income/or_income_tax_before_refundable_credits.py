from policyengine_us.model_api import *


class or_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "or_income_tax_before_credits", period
        )
        non_refundable_credits = tax_unit("or_non_refundable_credits", period)
        return max_(income_tax_before_credits - non_refundable_credits, 0)
