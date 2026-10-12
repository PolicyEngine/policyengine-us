from policyengine_us.model_api import *


class la_ccap_monthly_days(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Louisiana CCAP paid child care days per month"
    unit = "day"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = "la_ccap_eligible_child"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.payment
        days_per_week = person("childcare_days_per_week", period.this_year)
        hours_per_week = person("childcare_hours_per_week", period.this_year)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        days_from_days = days_per_week * weeks_per_month
        # Part-time hourly rates are not published; hours are prorated
        # against the 30-hour full-time threshold (LAC 28:CLXV.103).
        days_from_hours = p.max_monthly_days * min_(
            hours_per_week / p.full_time_weekly_hours, 1
        )
        # LAC 28:CLXV.103: full-time care (30+ hours per week) is paid in day
        # units up to 22 per month, while part-time care is paid hourly with
        # each day's total capped at the daily rate. Billing is therefore the
        # lesser of the day-based and hours-based units when both schedule
        # inputs are reported (a part-time schedule with attendance days must
        # not bill full-day units); a record reporting only one input is
        # billed on that input alone.
        has_days = days_per_week > 0
        has_hours = hours_per_week > 0
        day_units = where(has_days, days_from_days, p.max_monthly_days)
        hour_units = where(has_hours, days_from_hours, p.max_monthly_days)
        in_care = has_days | has_hours
        return where(
            in_care,
            min_(min_(day_units, hour_units), p.max_monthly_days),
            0,
        )
