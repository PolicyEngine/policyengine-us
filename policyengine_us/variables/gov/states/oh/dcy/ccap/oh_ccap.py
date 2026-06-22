from policyengine_us.model_api import *


class oh_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Ohio CCAP monthly subsidy"
    definition_period = MONTH
    defined_for = "oh_ccap_eligible"
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-05",
    )

    def formula(spm_unit, period, parameters):
        # 5180:6-1-10: each eligible child is reimbursed at the lower of the
        # add-on-adjusted county maximum rate or the provider's customary
        # charge (oh_ccap_rate_with_addons already applies this cap). The
        # family copayment (5180:2-16-05) is then subtracted.
        person = spm_unit.members
        is_eligible_child = person("oh_ccap_eligible_child", period)
        per_child_reimbursement = person("oh_ccap_rate_with_addons", period)
        total_reimbursement = spm_unit.sum(per_child_reimbursement * is_eligible_child)
        copay = spm_unit("oh_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
