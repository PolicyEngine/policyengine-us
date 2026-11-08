from policyengine_us.model_api import *


class co_ccap_capped_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = (
        "Colorado Child Care Assistance Program parent fee, capped at the reimbursement"
    )
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.124(K) and (L), PDF page 82: the fee pays the first
        # dollars of care and never exceeds the CCCAP reimbursement.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=82",
    )

    def formula(spm_unit, period, parameters):
        fee = spm_unit("co_ccap_parent_fee", period)
        reimbursement = spm_unit("co_ccap_reimbursement", period)
        return min_(fee, reimbursement)
