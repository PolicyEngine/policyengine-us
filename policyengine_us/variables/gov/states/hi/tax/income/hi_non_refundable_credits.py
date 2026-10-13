from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class hi_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # Form N-11 applies refundable credits first (line 33) and limits
        # nonrefundable credits (line 35) to the adjusted tax on line 34.
        "https://files.hawaii.gov/tax/forms/2025/n11_i.pdf#page=3",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=21",
    )

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.hi.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            ordered_credits,
            "hi_adjusted_tax_liability",
        )
