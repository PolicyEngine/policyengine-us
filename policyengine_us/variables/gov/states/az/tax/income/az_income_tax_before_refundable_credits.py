from policyengine_us.model_api import *


class az_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        before_non_refundable_credits = tax_unit(
            "az_income_tax_before_non_refundable_credits", period
        )
        non_refundable_credits = tax_unit("az_non_refundable_credits", period)
        return max_(before_non_refundable_credits - non_refundable_credits, 0)
