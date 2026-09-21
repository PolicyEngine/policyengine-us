"""Reconcile care-hour inputs for binary daily and weekly pricing categories."""

from policyengine_us.model_api import MONTHS_IN_YEAR, WEEKS_IN_YEAR, np, where

DAYS_IN_WEEK = 7


def _care_days_per_week(person, period):
    """Prefer weekly attendance; otherwise annualize monthly attendance."""
    weekly_days = person("childcare_days_per_week", period.this_year)
    monthly_days = person("childcare_attending_days_per_month", period.this_year)
    return where(
        weekly_days > 0, weekly_days, monthly_days * MONTHS_IN_YEAR / WEEKS_IN_YEAR
    )


def childcare_hours_for_daily_schedule(person, period):
    """Use daily hours or convert weekly hours using reported attendance.

    Without attendance frequency, weekly hours do not identify a daily
    category. Zero preserves the state's existing full-time fallback.
    These conversions are local to pricing: shared input variables stay intact.
    """
    daily_hours = person("childcare_hours_per_day", period.this_year)
    weekly_hours = person("childcare_hours_per_week", period.this_year)
    days = _care_days_per_week(person, period)
    converted_hours = np.divide(
        weekly_hours,
        days,
        out=np.zeros_like(weekly_hours),
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
