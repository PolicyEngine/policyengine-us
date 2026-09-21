from policyengine_us.model_api import *


class nj_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Jersey CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nj_ccap_eligible"
    reference = (
        "https://www.nj.gov/humanservices/notices/documents/rules-and-regulations/NJAC%2010_15%20CHILD%20CARE%20SERVICES.PDF#page=52",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=20",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("nj_ccap_copay", period)
        person = spm_unit.members
        # Reported care days or hours establish participation independently
        # of the missing-hours pricing fallback.
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        daily_hours = person("childcare_hours_per_day", period.this_year)
        monthly_days = person("childcare_attending_days_per_month", period.this_year)
        weekly_days = person("childcare_days_per_week", period.this_year)
        in_care = (
            (weekly_hours > 0)
            | (daily_hours > 0)
            | (monthly_days > 0)
            | (weekly_days > 0)
        )
        maximum_weekly_benefit = spm_unit.sum(
            person("nj_ccap_maximum_weekly_benefit", period) * in_care
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_benefit)
        ordinary_benefit = max_(capped_expenses - copay, 0)
        person = spm_unit.members
        eligible_child = person("nj_ccap_eligible_child", period)
        referred = person("nj_ccap_has_cpp_referral", period) & eligible_child
        has_referred_child = spm_unit.any(referred)
        ordinary_requirements = spm_unit("nj_ccap_income_eligible", period) & spm_unit(
            "nj_ccap_activity_eligible", period
        )
        payable = eligible_child & (referred | spm_unit.project(ordinary_requirements))
        # Referral eligibility belongs to the referred child. Siblings still
        # need the ordinary family requirements to contribute to the payment.
        child_expense = person("pre_subsidy_childcare_expenses", period)
        # The default person-level allocation spreads the SPM-unit expense only
        # across children under 18, so a payable child with no reported expense
        # (such as a referred 18-year-old) takes an equal share of the SPM-unit
        # expense not already attributed to any person. When person-level
        # expenses are supplied nothing is unattributed, so results are
        # unchanged and no expense is counted twice.
        unattributed_expense = max_(
            pre_subsidy_childcare_expenses - spm_unit.sum(child_expense), 0
        )
        needs_fallback = payable & in_care & (child_expense == 0)
        fallback_count = spm_unit.sum(needs_fallback)
        fallback_share = np.divide(
            unattributed_expense,
            fallback_count,
            out=np.zeros_like(unattributed_expense),
            where=fallback_count > 0,
        )
        child_expense = where(
            needs_fallback, spm_unit.project(fallback_share), child_expense
        )
        child_maximum = person("nj_ccap_maximum_weekly_benefit", period) * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        referred_expense = spm_unit.sum(
            min_(child_expense, child_maximum) * payable * in_care
        )
        return where(
            has_referred_child, max_(referred_expense - copay, 0), ordinary_benefit
        )
