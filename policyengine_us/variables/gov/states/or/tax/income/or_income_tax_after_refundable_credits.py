from policyengine_us.model_api import *


class or_income_tax_after_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income tax after refundable credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income_tax_after_non_refundable_credits = tax_unit(
            "or_income_tax_after_non_refundable_credits", period
        )
        refundable_credits = tax_unit("or_refundable_credits", period)
        return income_tax_after_non_refundable_credits - refundable_credits
