from policyengine_us.model_api import *


class wv_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "West Virginia CCAP benefit amount"
    definition_period = MONTH
    defined_for = "wv_ccap_eligible"
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=79",
        "https://bfa.wv.gov/media/39915/download?inline#page=41",
    )

    def formula(spm_unit, period, parameters):
        # Manual §7.2.7.3-7.2.7.4: Monthly Rate = 20 × daily when 13-20 days/month
        # of attendance; per-day billing otherwise. Reimbursement is also capped
        # at the actual provider charge.
        p = parameters(period).gov.states.wv.dhhr.ccap.billing
        person = spm_unit.members
        daily_benefit = person("wv_ccap_daily_benefit", period)
        days_per_week = person("childcare_days_per_week", period.this_year)
        actual_days = days_per_week * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        in_monthly_range = (actual_days >= p.monthly_rate_min_days) & (
            actual_days <= p.monthly_rate_max_days
        )
        billed_days = where(in_monthly_range, p.monthly_rate_max_days, actual_days)
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = min_(
            daily_benefit * billed_days, pre_subsidy_per_child
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("wv_ccap_copay", period)
        pre_subsidy_total = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        return min_(max_(pre_subsidy_total - copay, 0), total_reimbursement)
