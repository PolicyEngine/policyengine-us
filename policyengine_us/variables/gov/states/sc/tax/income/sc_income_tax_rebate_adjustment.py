from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class sc_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "SC income tax rebate adjustment"
    documentation = (
        "Actual reduction in SC income tax from its registered "
        "nonrefundable rebate, after other credits and the final zero floor. "
        "Other credit amounts and filing choices remain fixed."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.sc.tax.income.credits.non_refundable
        if "sc_2022_rebate" not in credits:
            return 0
        other_credits = [credit for credit in credits if credit != "sc_2022_rebate"]
        tax_variable = "sc_income_tax_before_non_refundable_credits"
        without_rebate = ordered_capped_state_non_refundable_credits(
            tax_unit, period, other_credits, tax_variable
        )
        with_rebate = tax_unit("sc_non_refundable_credits", period)
        tax_before_credits = tax_unit(tax_variable, period)
        return max_(tax_before_credits - without_rebate, 0) - max_(
            tax_before_credits - with_rebate, 0
        )
