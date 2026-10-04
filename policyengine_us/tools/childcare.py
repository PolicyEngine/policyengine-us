"""Reconcile care-hour inputs for binary daily and weekly pricing categories."""

from policyengine_us.model_api import MONTHS_IN_YEAR, WEEKS_IN_YEAR, np, where

DAYS_IN_WEEK = 7


def _care_days_per_week(person, period):
    """Prefer weekly attendance; otherwise annualize monthly attendance.

    Reported weekly days take precedence and are never rounded. Monthly
    attendance is annualized with 12/52, but calendar months have 20 to 23
    weekdays, so that ratio never yields exactly five days a week (20 days
    give 4.6, 22 give 5.1). Without rounding, a five-weekday schedule sitting
    on a legal threshold (5 h/day in KY/WY, 20 h/wk in TN/WI, 7 h/day in AR)
    would flip pricing category, so derived weekly days of at least one day
    are rounded to whole days. Sparser attendance keeps its fractional weekly
    average so weekly hours still concentrate on the actual care days.
    """
    weekly_days = person("childcare_days_per_week", period.this_year)
    monthly_days = person("childcare_attending_days_per_month", period.this_year)
    derived_days = monthly_days * MONTHS_IN_YEAR / WEEKS_IN_YEAR
    rounded_days = where(derived_days >= 1, np.round(derived_days), derived_days)
    return where(weekly_days > 0, weekly_days, rounded_days)


def childcare_hours_for_daily_schedule(person, period):
    """Use daily hours or convert weekly hours for a binary pricing category.

    With no reported attendance frequency, the weekly hours give an upper
    bound on hours in any single care day (care occurs on at least one day
    per week): classify as part day only when that bound is in the state's
    part-day range. Otherwise retain full-time pricing. This bound is not
    actual daily care hours and must not be used for hourly payments or
    attendance calculations. These conversions are local to pricing: shared
    input variables stay intact.
    """
    daily_hours = person("childcare_hours_per_day", period.this_year)
    weekly_hours = person("childcare_hours_per_week", period.this_year)
    days = _care_days_per_week(person, period)
    converted_hours = np.divide(
        weekly_hours,
        days,
        out=weekly_hours.copy(),
        where=days > 0,
    )
    return where(daily_hours > 0, daily_hours, converted_hours)


def childcare_hours_for_weekly_schedule(person, period):
    """Use weekly hours or convert daily hours for a binary pricing category.

    With no reported attendance frequency, seven days gives an upper bound:
    classify as part time only when that bound is in the state's part-time range.
    Otherwise retain full-time pricing. This bound is not actual care hours
    and must not be used for hourly payments or attendance calculations.
    """
    weekly_hours = person("childcare_hours_per_week", period.this_year)
    daily_hours = person("childcare_hours_per_day", period.this_year)
    days = _care_days_per_week(person, period)
    converted_hours = daily_hours * where(days > 0, days, DAYS_IN_WEEK)
    return where(weekly_hours > 0, weekly_hours, converted_hours)
