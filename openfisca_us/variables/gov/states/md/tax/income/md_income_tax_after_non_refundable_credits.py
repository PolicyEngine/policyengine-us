from openfisca_us.model_api import *


class md_income_tax_after_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax after non-refundable credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        non_refundable_credits = parameters(
            period
        ).gov.states.md.tax.income.credits.non_refundable
        total_non_refundable_credits = add(
            tax_unit, period, non_refundable_credits
        )
        return max_(0, tax_before_credits - total_non_refundable_credits)
