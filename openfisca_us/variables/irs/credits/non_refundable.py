from openfisca_us.model_api import *


class c07100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax non-refundable credits"
    documentation = (
        "Total non-refundable credits used to reduce positive tax liability"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        credits = parameters(period).irs.credits.non_refundable
        return add(tax_unit, period, credits)


income_tax_non_refundable_credits = variable_alias(
    "income_tax_non_refundable_credits", c07100
)
