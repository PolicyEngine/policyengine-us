from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class ny_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY capped non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.ny.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit, period, credits, "ny_income_tax_before_credits"
        )
