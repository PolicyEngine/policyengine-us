from policyengine_us.model_api import *


class household_state_income_tax(Variable):
    # This definition contains all modelled states, and exists to solve circular dependencies in state_income_tax.
    value_type = float
    entity = TaxUnit
    label = "household State tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        default_tax = add(
            tax_unit,
            period,
            ["state_income_tax_before_refundable_credits"],
        ) - add(tax_unit, period, ["state_refundable_credits"])
        state_code = tax_unit.household("state_code", period)
        return where(
            state_code == StateCode.WI,
            tax_unit("wi_income_tax", period),
            default_tax,
        )
