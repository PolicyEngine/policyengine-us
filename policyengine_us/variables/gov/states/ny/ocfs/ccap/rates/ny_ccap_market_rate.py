from policyengine_us.model_api import *


class ny_ccap_market_rate(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP monthly market rate"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "The applicable market rate ceiling for one child, converted to a "
        "monthly amount. Under 18 NYCRR 415.9(d) care exceeding one weekly or "
        "daily period earns an additional period, priced at the rate for the "
        "amount of time that period covers: the daily rate at or above the "
        "daily minimum hours, the part-day rate below it. A weekly schedule "
        "earns one additional period per day past the weekly maximum days, "
        "and any schedule earns one on each day of care at or above the daily "
        "maximum hours."
    )
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=6",
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=45",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap
        county_group = person.household("ny_ccap_county_group", period.this_year)
        provider_type = person("childcare_provider_type_group", period.this_year)
        age_group = person("ny_ccap_age_group", period.this_year)
        duration = person("ny_ccap_duration_of_care", period.this_year)
        durations = duration.possible_values
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        days_per_week = person("childcare_days_per_week", period.this_year)
        weekly_rate = p.rates.weekly[county_group][provider_type][age_group]
        daily_rate = p.rates.daily[county_group][provider_type][age_group]
        part_day_rate = p.rates.part_day[county_group][provider_type][age_group]
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
