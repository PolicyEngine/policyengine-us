from policyengine_us.model_api import *


class eitc_relevant_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC-relevant investment income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        no_loss_capital_gains = max_(
            0,
            add(tax_unit, period, ["capital_gains"]),
        )
        return (
            add(
                tax_unit,
                period,
                ["net_investment_income", "tax_exempt_interest_income"],
            )
            # Replace limited-loss capital gains with no-loss capital gains.
            - tax_unit("c01000", period)  # Limited-loss capital gains.
            + no_loss_capital_gains
        )
