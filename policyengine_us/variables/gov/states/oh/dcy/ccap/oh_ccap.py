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
        # charge. oh_ccap_rate_with_addons is defined_for oh_ccap_eligible_child,
        # so it returns 0 for non-eligible children and the sum needs no further
        # masking. The family copayment (5180:2-16-05) is then subtracted.
        total_reimbursement = add(spm_unit, period, ["oh_ccap_rate_with_addons"])
        copay = spm_unit("oh_ccap_copay", period)
        # 5180:2-16-05(H): the family pays the lesser of the copayment or the
        # cost of care, so the subtracted copay is capped at the eligible
        # children's total customary charge.
        person = spm_unit.members
        eligible_child = person("oh_ccap_eligible_child", period)
        cost_of_care = spm_unit.sum(
            eligible_child * person("pre_subsidy_childcare_expenses", period)
        )
        capped_copay = min_(copay, cost_of_care)
        return max_(total_reimbursement - capped_copay, 0)
