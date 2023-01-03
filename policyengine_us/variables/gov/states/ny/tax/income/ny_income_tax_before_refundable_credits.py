from policyengine_us.model_api import *


class ny_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "ny_income_tax_before_credits", period
        )
        non_refundable_credits = tax_unit("ny_non_refundable_credits", period)
        return max_(income_tax_before_credits - non_refundable_credits, 0)
