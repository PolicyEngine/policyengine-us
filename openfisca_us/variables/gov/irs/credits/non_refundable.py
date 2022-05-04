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


class income_tax_capped_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable tax credits"
    unit = USD
    documentation = "Capped value of non-refundable tax credits"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("income_tax_before_credits", period),
            tax_unit("income_tax_non_refundable_credits", period),
        )
