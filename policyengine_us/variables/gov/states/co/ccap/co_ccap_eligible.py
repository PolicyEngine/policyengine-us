from policyengine_us.model_api import *


class co_ccap_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "Eligible for Colorado Child Care Assistance Program"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=31",
    )
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        in_entry_process = spm_unit("co_ccap_is_in_entry_process", period)
        entry_eligible = spm_unit("co_ccap_entry_eligible", period)
        in_re_determination_process = spm_unit(
            "co_ccap_is_in_re_determination_process", period
        )
        re_determination_eligible = spm_unit(
            "co_ccap_re_determination_eligible", period
        )

        return (in_entry_process & entry_eligible) | (
            in_re_determination_process & re_determination_eligible
        )
