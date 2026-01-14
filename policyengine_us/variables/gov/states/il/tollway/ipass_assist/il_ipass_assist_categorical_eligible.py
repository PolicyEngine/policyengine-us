from policyengine_us.model_api import *


class il_ipass_assist_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Illinois I-PASS Assist categorically eligible"
    reference = (
        "https://agency.illinoistollway.com/assist",
        "https://www.dhs.state.il.us/page.aspx?item=150431",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Check for actual benefit receipt (snap > 0, il_tanf > 0, il_aabd > 0)
        snap_recipient = spm_unit("snap", period) > 0
        tanf_recipient = spm_unit("il_tanf", period) > 0
        aabd_recipient = spm_unit("il_aabd", period) > 0
        return snap_recipient | tanf_recipient | aabd_recipient
