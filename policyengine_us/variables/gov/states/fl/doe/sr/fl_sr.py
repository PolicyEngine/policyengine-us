from policyengine_us.model_api import *


class fl_sr(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Florida School Readiness program benefit"
    definition_period = MONTH
    defined_for = "is_fl_sr_eligible"
    reference = (
        "https://flrules.elaws.us/fac/6m-4.400",
        "https://www.flsenate.gov/laws/statutes/2025/1002.84",
        "https://flrules.elaws.us/fac/6m-4.500",
    )

    def formula(spm_unit, period, parameters):
        # spm_unit_pre_subsidy_childcare_expenses is YEAR-defined; the bare
        # monthly period auto-divides the annual amount to a monthly value.
        monthly_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("fl_sr_copay", period)
        # Cap the subsidy at the statewide maximum reimbursement rate
        # (6M-4.500; SPB 2502 FY2025-26): each eligible child's daily rate times
        # attendance days, summed across the unit. A county with no
        # published rate (an unknown / non-Florida county_str) yields a zero cap
        # and therefore a zero subsidy -- there is no published rate to pay
        # against, so the benefit is not provided.
        person = spm_unit.members
        daily_rate = person("fl_sr_max_daily_rate", period)
        # Rule 6M-4.500(1)(d), F.A.C.: providers are reimbursed for each
        # documented attendance day at the full-time or part-time rate, so a
        # reported weekly schedule implies paid attendance days. When monthly
        # days are not reported, derive them from weekly care days (52 weeks
        # over 12 months); hours-only inputs still yield no attendance days.
        monthly_days = person("childcare_attending_days_per_month", period.this_year)
        weekly_days = person("childcare_days_per_week", period.this_year)
        derived_monthly_days = weekly_days * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        attending_days = where(monthly_days > 0, monthly_days, derived_monthly_days)
        is_eligible_child = person("is_fl_sr_child_eligible", period)
        monthly_cap = spm_unit.sum(daily_rate * attending_days * is_eligible_child)
        capped_expenses = min_(monthly_expenses, monthly_cap)
        return max_(capped_expenses - copay, 0)
