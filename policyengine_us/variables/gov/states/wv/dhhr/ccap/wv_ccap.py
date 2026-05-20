from policyengine_us.model_api import *


class wv_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "West Virginia CCAP benefit amount"
    definition_period = MONTH
    defined_for = "wv_ccap_eligible"
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=80",
        "https://bfa.wv.gov/media/39915/download?inline#page=41",
    )

    def formula(spm_unit, period, parameters):
        # Manual §7.2.7.3-7.2.7.4: Monthly Rate = 20 × base daily rate when
        # 13-20 days/month of attendance; per-day billing otherwise.
        # Manual §7.2.7.2: rate supplements (special needs, shift differential)
        # are paid for actual days of care only — the monthly rate does NOT
        # apply to rate supplements.
        p = parameters(period).gov.states.wv.dhhr.ccap
        person = spm_unit.members
        weekly_care_days = person("childcare_days_per_week", period.this_year)
        monthly_care_days = weekly_care_days * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        in_monthly_range = (monthly_care_days >= p.billing.monthly_rate_min_days) & (
            monthly_care_days <= p.billing.monthly_rate_max_days
        )
        base_billed_days = where(
            in_monthly_range,
            p.billing.monthly_rate_max_days,
            monthly_care_days,
        )
        daily_rate = person("wv_ccap_daily_rate", period)
        is_disabled = person("is_disabled", period.this_year)
        special_needs_supplement = where(is_disabled, p.supplements.special_needs, 0)
        non_trad = person("wv_ccap_non_traditional_hours", period)
        non_trad_supplement = where(non_trad, p.supplements.non_traditional_hours, 0)
        daily_supplement = special_needs_supplement + non_trad_supplement
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = min_(
            daily_rate * base_billed_days + daily_supplement * monthly_care_days,
            pre_subsidy_per_child,
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("wv_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
