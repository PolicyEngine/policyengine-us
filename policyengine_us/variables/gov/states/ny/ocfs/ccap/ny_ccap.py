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
        child_count = spm_unit.sum(counted)
        total_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        # Only eligible children actually in care draw on the unit's child
        # care expenses; the shared per-person proration spreads them across
        # every child under 18.
        per_child_expenses = where(
            child_count > 0, total_expenses / max_(child_count, 1), 0
        )
        # 18 NYCRR 415.6(e)(1) and (e)(3): payments do not exceed the actual
        # cost of care, and payments per child do not exceed the applicable
        # rate for the type of provider used and the age of the child. Capping
        # per child rather than on pooled totals stops one child's unused rate
        # headroom from absorbing a sibling's above-rate expenses.
        reimbursable_care = spm_unit.sum(
            min_(spm_unit.project(per_child_expenses), market_rate) * counted
        )
        family_share = spm_unit("ny_ccap_family_share", period)
        return max_(reimbursable_care - family_share, 0)
