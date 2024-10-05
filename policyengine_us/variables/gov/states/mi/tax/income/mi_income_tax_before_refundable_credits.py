from policyengine_us.model_api import *


class mi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan income tax before refundable credits"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_before_non_refundable_credits = tax_unit(
            "mi_income_tax_before_non_refundable_credits", period
        )
        non_refundable_credits = tax_unit("mi_non_refundable_credits", period)
        return max_(
            tax_before_non_refundable_credits - non_refundable_credits, 0
        )
