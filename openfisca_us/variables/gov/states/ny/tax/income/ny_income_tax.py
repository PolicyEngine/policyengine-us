from openfisca_us.model_api import *


class ny_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax"
    unit = USD
    documentation = "Description"
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("ny_income_tax_before_credits", period)
        non_refundable_credits = tax_unit("ny_non_refundable_credits", period)
        refundable = parameters(
            period
        ).gov.states.ny.tax.income.credits.refundable
        refundable_credits = add(tax_unit, period, refundable)
        return income_tax - non_refundable_credits - refundable_credits
