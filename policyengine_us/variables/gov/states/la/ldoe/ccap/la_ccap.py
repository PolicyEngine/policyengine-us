from policyengine_us.model_api import *


class la_ccap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana Child Care Assistance Program benefit"
    unit = USD
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.payment
        person = spm_unit.members
        eligible_child = person("la_ccap_eligible_child", period)
        daily_rate = person("la_ccap_daily_rate", period)
        days_per_week = person("childcare_days_per_week", period.this_year)
        hours_per_week = person("childcare_hours_per_week", period.this_year)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        days_from_days = days_per_week * weeks_per_month
        # Part-time hourly rates are not published; when only hours are
        # provided, prorate the monthly day maximum by the share of the
        # 30-hour full-time threshold (LAC 28:CLXV.103).
        days_from_hours = p.max_monthly_days * min_(
            hours_per_week / p.full_time_weekly_hours, 1
        )
        monthly_days = min_(
            where(days_per_week > 0, days_from_days, days_from_hours),
            p.max_monthly_days,
        )
        # The sliding fee scale co-payment is per child per day; waivers
        # (homelessness, disability, Head Start, STEP) zero it through
        # la_ccap_copay_waived.
        unit_copay = spm_unit("la_ccap_daily_copay", period)
        child_copay = spm_unit.project(unit_copay)
        monthly_expense = person("pre_subsidy_childcare_expenses", period)
        capped_charge = min_(monthly_expense, daily_rate * monthly_days)
        per_child = max_(capped_charge - child_copay * monthly_days, 0)
        return spm_unit.sum(per_child * eligible_child)
