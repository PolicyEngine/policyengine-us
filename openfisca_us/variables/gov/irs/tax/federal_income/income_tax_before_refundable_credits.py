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
        return income_tax_bc - capped_credits


income_tax_before_refundable_credits = variable_alias(
    "income_tax_before_refundable_credits", c09200
)
