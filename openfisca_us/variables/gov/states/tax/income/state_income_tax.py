from openfisca_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax"
    unit = USD
    definition_period = YEAR

    def formula_2021(tax_unit, period, parameters):
        before_refundable_credits = tax_unit(
            "state_income_tax_before_refundable_credits", period
        )
        refundable_credits = tax_unit(
            "state_income_tax_refundable_credits", period
        )
        return before_refundable_credits - refundable_credits
