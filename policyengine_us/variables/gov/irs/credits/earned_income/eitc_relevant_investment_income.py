from policyengine_us.model_api import *


class eitc_relevant_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC-relevant investment income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        no_loss_capital_gains = max_(0, tax_unit("net_capital_gains", period))
        return (
            add(
                tax_unit,
                period,
                ["net_investment_income", "tax_exempt_interest_income"],
            )
            # replace limited-loss capital gains with no-loss capital gains
            - tax_unit("loss_limited_net_capital_gains", period)
            + no_loss_capital_gains
        )
