from policyengine_us.model_api import *


class co_ccap_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.103(UU), 3.111(F), 3.124(K) and (L), 3.125(FFF) and
        # 3.132(D) and (E), PDF pages 9, 35, 82, 101, 126
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=9",
    )

    def formula(spm_unit, period, parameters):
        # The county pays the lesser of each eligible child's charges and the
        # county rate for that child's care (3.125(FFF), 3.130), less the
        # parent fee, which pays the first dollars (3.124(K)) and never
        # exceeds the reimbursement (3.124(L)). Eligible children are those
        # 3.132(D) and (E) cover: children under 13, and children under 19
        # who can't care for themselves or who are under court supervision
        # (3.103(UU), 3.111(F)). A member outside those limits adds nothing.
        reimbursement = spm_unit("co_ccap_reimbursement", period)
        parent_fee = spm_unit("co_ccap_capped_parent_fee", period)
        return max_(reimbursement - parent_fee, 0)
