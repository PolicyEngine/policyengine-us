from openfisca_us.model_api import *


class state_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax before refundable credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit(
            "state_income_tax_before_credits", period
        )
        non_refundable_credits = tax_unit(
            "state_income_tax_non_refundable_credits", period
        )
        return tax_before_credits - non_refundable_credits
