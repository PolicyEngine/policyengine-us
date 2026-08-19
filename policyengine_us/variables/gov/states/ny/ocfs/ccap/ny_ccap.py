from policyengine_us.model_api import *


class ny_ccap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York Child Care Assistance Program benefit"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=39",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        market_rate = person("ny_ccap_market_rate", period)
        # ny_ccap_eligible_child carries New York's income test as well as the
        # categorical routes that waive it, so no separate income gate is
        # applied here.
        eligible = person("ny_ccap_eligible_child", period)
        in_care = person("childcare_hours_per_day", period.this_year) > 0
        counted = eligible & in_care
        # The unit's expenses are shared across every child in paid care, so
        # an ineligible child's share stays with that child rather than
        # raising an eligible sibling against its own rate ceiling.
        children_in_care = spm_unit.sum(in_care)
        total_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        per_child_expenses = total_expenses / max_(children_in_care, 1)
        # 18 NYCRR 415.6(e)(1) and (e)(3): payments do not exceed the actual
        # cost of care, and payments per child do not exceed the applicable
        # rate for the type of provider used and the age of the child. Capping
        # per child rather than on pooled totals stops one child's unused rate
        # headroom from absorbing a sibling's above-rate expenses.
        reimbursable_care = spm_unit.sum(
            min_(spm_unit.project(per_child_expenses), market_rate) * counted
        )
        # 415.3(e)(5): one family share per family regardless of the number of
        # children receiving care, so it is subtracted once from the total.
        family_share = spm_unit("ny_ccap_family_share", period)
        return max_(reimbursable_care - family_share, 0)
