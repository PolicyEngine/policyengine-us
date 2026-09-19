from policyengine_us.model_api import *


class nj_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Jersey CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nj_ccap_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-15-5-2",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=14",
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
        return max_(capped_expenses - copay, 0)
