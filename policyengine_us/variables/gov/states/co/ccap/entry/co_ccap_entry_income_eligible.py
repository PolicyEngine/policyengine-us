from policyengine_us.model_api import *


class co_ccap_entry_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the entry of Colorado Child Care Assistance Program through income"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19"
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        fpg_eligible = spm_unit("co_ccap_fpg_eligible", period)
        smi_eligible = spm_unit("co_ccap_smi_eligible", period)
        return fpg_eligible & smi_eligible
