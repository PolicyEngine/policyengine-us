from openfisca_us.model_api import *


class il_income_tax_after_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax after nonrefundable credits"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "il_income_tax_before_nonrefundable_credits", period
        )
        nonrefundable_credits = tax_unit("il_nonrefundable_credits", period)

        return income_tax_before_credits - nonrefundable_credits
