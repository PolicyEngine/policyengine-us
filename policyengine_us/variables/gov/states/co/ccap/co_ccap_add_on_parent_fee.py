from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parent_fee_arithmetic import (
    income_and_guideline_in_cents,
)


class co_ccap_add_on_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program add on parent fee"
    documentation = (
        "The fee for each child in care after the first, charged when gross "
        "countable income exceeds the federal poverty guideline."
    )
    reference = (
        # PDF pages 83-84
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=83",
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap.parent_fee
        income, fpg = income_and_guideline_in_cents(spm_unit, period)
        children_in_care = spm_unit("co_ccap_children_in_care", period)
        additional_children = max_(children_in_care - 1, 0)
        return additional_children * p.add_on * (income > fpg)
