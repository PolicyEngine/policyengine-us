from policyengine_us.model_api import *


class nyc_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "nyc_income_tax_before_credits", period
        )
        non_refundable_credits = tax_unit("nyc_non_refundable_credits", period)
        return max_(income_tax_before_credits - non_refundable_credits, 0)
