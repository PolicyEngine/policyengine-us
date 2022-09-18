from openfisca_us.model_api import *


class ny_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY capped non-refundable tax credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        credits = parameters(
            period
        ).gov.states.ny.tax.income.credits.non_refundable
        income_tax = tax_unit("ny_income_tax_before_credits", period)
        total_credit_value = add(tax_unit, period, credits)
        return min_(
            income_tax,
            total_credit_value,
        )
