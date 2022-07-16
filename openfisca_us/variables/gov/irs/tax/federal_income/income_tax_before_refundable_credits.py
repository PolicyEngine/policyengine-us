from openfisca_us.model_api import *


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Income tax before refundable credits"
    documentation = "Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"

    def formula(tax_unit, period, parameters):
        income_tax_bc = tax_unit("income_tax_before_credits", period)
        capped_credits = tax_unit(
            "income_tax_capped_non_refundable_credits", period
        )
        taxes_net_nonrefundable_credits = income_tax_bc - capped_credits
        other_taxes = add(
            tax_unit, period, ["niit", "e09700", "e09800", "e09900"]
        )
        return taxes_net_nonrefundable_credits + other_taxes


income_tax_before_refundable_credits = variable_alias(
    "income_tax_before_refundable_credits", c09200
)
