from policyengine_us.model_api import *


class co_ccap_entry_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for the entry of the Colorado Child Care Assistance Program"
    )
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("co_ccap_entry_income_eligible", period)
        has_eligible_children = (
            spm_unit("co_ccap_eligible_children", period) > 0
        )
        return income_eligible & has_eligible_children
