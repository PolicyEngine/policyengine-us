from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parent_fee_arithmetic import (
    drop_cents,
    income_and_guideline_in_cents,
)


class co_ccap_base_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program base parent fee"
    documentation = (
        "The parent fee on gross countable income, in whole dollars, before "
        "the fee for additional children, the part-time rate and the quality "
        "discount. Through July 2028 counties charge 1% of income plus 14% of "
        "income above the federal poverty guideline; from August 2028 they "
        "charge marginal rates of 1%, 3%, 5% and 7%."
    )
    reference = (
        # PDF pages 82-84
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=82",
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap.parent_fee
        # Families with no income pay no fee (section 3.124(I)(7)); a net loss
        # counts as no income.
        income, fpg = income_and_guideline_in_cents(spm_unit, period)
        income_to_fpg = np.zeros_like(income)
        has_fpg = fpg > 0
        income_to_fpg[has_fpg] = income[has_fpg] / fpg[has_fpg]
        return drop_cents(
            p.income_rate * income + p.marginal_rate.calc(income_to_fpg) * fpg
        )
