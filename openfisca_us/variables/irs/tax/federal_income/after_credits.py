from openfisca_us.model_api import *


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Income tax before refundable credits"
    documentation = "Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"

    def formula(tax_unit, period, parameters):
        return max_(
            0,
            tax_unit("income_tax_before_credits", period)
            - tax_unit("income_tax_non_refundable_credits", period),
        )


income_tax_before_refundable_credits = variable_alias(
    "income_tax_before_refundable_credits", c09200
)


class iitax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Federal income tax"
    documentation = "Total federal individual income tax liability."

    def formula(tax_unit, period, parameters):
        return tax_unit(
            "income_tax_before_refundable_credits", period
        ) - tax_unit("income_tax_refundable_credits", period)


income_tax = variable_alias("income_tax", iitax)
