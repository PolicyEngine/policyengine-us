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
        # We don't track per-day attendance hours at the moment, so every
        # attended day is paid at the full-day rate; the part-day conversion
        # (§7.2.7.6 — 2/3 rate for 2-4 hrs, 1/3 for < 2 hrs), the full-day
        # 4-hr minimum (§7.2.7.5), the 18-hour daily cap (§7.2.1), and the
        # two-provider-per-child billing rule (§6.4.2, §7.2.3, §7.2.5) are
        # not modeled.
        p = parameters(period).gov.states.wv.dhhr.ccap
        person = spm_unit.members
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        in_monthly_range = (monthly_care_days >= p.billing.monthly_rate_min_days) & (
            monthly_care_days <= p.billing.monthly_rate_max_days
        )
        daily_rate = person("wv_ccap_daily_rate", period)
        has_developmental_delay = person("has_developmental_delay", period.this_year)
        special_needs_supplement = where(
            has_developmental_delay, p.supplements.special_needs, 0
        )
        non_trad = person("wv_ccap_non_traditional_hours", period)
        non_trad_supplement = where(non_trad, p.supplements.non_traditional_hours, 0)
        daily_supplement = special_needs_supplement + non_trad_supplement
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        monthly_rate_maximum = (
            daily_rate * p.billing.monthly_rate_max_days
            + daily_supplement * monthly_care_days
        )
        per_day_maximum = person("wv_ccap_daily_benefit", period) * monthly_care_days
        per_child_reimbursement = min_(
            pre_subsidy_per_child,
            where(in_monthly_range, monthly_rate_maximum, per_day_maximum),
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("wv_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
