from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class va_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia non-refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.va.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            ordered_credits,
            "va_income_tax_before_non_refundable_credits",
        )
