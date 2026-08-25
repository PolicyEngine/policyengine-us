from policyengine_us.model_api import *


class ut_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Utah CCAP benefit amount"
    definition_period = MONTH
    defined_for = "ut_ccap_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-713",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-707",
    )

    def formula(spm_unit, period, parameters):
        # R986-700-713 pays each child's care at the lower of the provider's
        # actual established rate (proxied by the child's share of billed
        # child care expenses) and that child's Table 3 local market rate
        # cap; the summed per-child payments are reduced by the family
        # co-payment, floored at zero. The hourly-unit-cost payment path and
        # the CCQS Enhanced Subsidy Grant (R986-700-742) are not modeled.
        person = spm_unit.members
        is_eligible_child = person("ut_ccap_eligible_child", period)
        market_rate = person("ut_ccap_market_rate", period)
        pre_subsidy_expense = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = (
            min_(pre_subsidy_expense, market_rate) * is_eligible_child
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("ut_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
