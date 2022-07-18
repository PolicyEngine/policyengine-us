from openfisca_us.model_api import *


class md_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_after_non_refundable_credits = tax_unit(
            "md_income_tax_after_non_refundable_credits", period
        )
        refundable_credits = parameters(
            period
        ).gov.states.md.tax.income.credits.refundable
        total_refundable_credits = add(tax_unit, period, refundable_credits)
        return tax_after_non_refundable_credits - total_refundable_credits
