from policyengine_us.model_api import *


class wv_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia income tax before refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit(
            "wv_income_tax_before_non_refundable_credits", period
        )
        credits = tax_unit("wv_non_refundable_credits", period)
        return max_(tax_before_credits - credits, 0)
