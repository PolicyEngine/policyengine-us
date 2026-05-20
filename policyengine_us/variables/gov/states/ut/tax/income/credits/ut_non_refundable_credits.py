from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class ut_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ut.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            ordered_credits,
            "ut_income_tax_before_non_refundable_credits",
        )
