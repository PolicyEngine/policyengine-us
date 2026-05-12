from policyengine_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income_tax_before_refundable_credits = add(
            tax_unit,
            period,
            ["state_income_tax_before_refundable_credits"],
        )
        refundable_credits = add(tax_unit, period, ["state_refundable_credits"])
        default_tax = income_tax_before_refundable_credits - refundable_credits
        state_code = tax_unit.household("state_code", period)
        return where(
            state_code == StateCode.WI,
            tax_unit("wi_income_tax", period),
            default_tax,
        )
