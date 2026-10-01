from policyengine_us.model_api import *


class ne_liheap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP gross countable earned income"
    defined_for = StateCode.NE
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/NE_Plan_2026.pdf#page=7",
        "https://rules.nebraska.gov/rules?agencyId=37&titleId=230",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        countable = person("snap_countable_earner", period.first_month)
        included = person("is_snap_immigration_status_eligible", period.first_month)
        size = spm_unit("ne_liheap_household_size", period)
        # 475 NAC 3-002.06(A)-(B), incorporated by 476 NAC 2-002.01:
        # prorate excluded members' countable income across all members and
        # retain the eligible members' shares. Eligible members count in full.
        fraction = size / max_(spm_unit("spm_unit_size", period), 1)
        share = where(included, 1, spm_unit.project(fraction))
        # 475 NAC 3-002.04(B)(i) counts each source of self-employment, so
        # existing net business and farm inputs are read, each floored at zero,
        # without another business expense deduction. The special farm-loss
        # offset requires tax-return evidence and at least $1,000 of gross farm
        # income, which existing inputs cannot establish. That offset, Nebraska's
        # tax-return/49%-ledger distinction, and capital gains from business
        # assets are not modeled here.
        earned = (
            max_(person("employment_income", period), 0)
            + max_(person("self_employment_income", period), 0)
            + max_(person("sstb_self_employment_income", period), 0)
            + max_(person("farm_operations_income", period), 0)
        )
        return spm_unit.sum(earned * countable * share)
