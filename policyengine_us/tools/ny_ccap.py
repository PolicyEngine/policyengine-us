from policyengine_us.model_api import *


def ny_ccap_monthly_rate(
    person, period, parameters, weekly_rate, daily_rate, part_day_rate
):
    """Price the scheduled and excess care periods under 24-OCFS-LCM-22."""
    p = parameters(period).gov.states.ny.ocfs.ccap
    duration = person("ny_ccap_duration_of_care", period.this_year)
    durations = duration.possible_values
    hours_per_day = person("childcare_hours_per_day", period.this_year)
    days_per_week = person("childcare_days_per_week", period.this_year)
    base_rate = select(
        [
            duration == durations.WEEKLY,
            duration == durations.DAILY,
            duration == durations.PART_DAY,
        ],
        [
            weekly_rate,
            daily_rate * days_per_week,
            part_day_rate * days_per_week,
        ],
        default=0,
    )
    # A weekly rate covers the weekly maximum days; each further day is an
    # additional period priced by that day's own hours.
    excess_days = where(
        duration == durations.WEEKLY,
        max_(days_per_week - p.duration.weekly_maximum_days, 0),
        0,
    )
    excess_day_rate = where(
        hours_per_day >= p.duration.daily_minimum_hours,
        daily_rate,
        part_day_rate,
    )
    # 24-OCFS-LCM-22 sec. III.4: care of 12 hours or more in a day earns
    # one further period on each day, priced by the time over 12 hours,
    # so a day of exactly 12 hours draws the part-day rate.
    reaches_daily_maximum = hours_per_day >= p.duration.daily_maximum_hours
    excess_hours = max_(hours_per_day - p.duration.daily_maximum_hours, 0)
    excess_hour_rate = where(
        excess_hours >= p.duration.daily_minimum_hours,
        daily_rate,
        part_day_rate,
    )
    excess_hour_periods = where(reaches_daily_maximum, days_per_week, 0)
    rate_per_week = (
        base_rate
        + excess_days * excess_day_rate
        + excess_hour_periods * excess_hour_rate
    )
    return rate_per_week * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
