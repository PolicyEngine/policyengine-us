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
        "monthly amount. Under 18 NYCRR 415.9(b) a weekly schedule running "
        "beyond the weekly maximum days earns an additional period for each "
        "extra day, priced at the weekly rate divided by the weekly maximum "
        "days."
    )
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=14",
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=45",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap
        county_group = person.household("ny_ccap_county_group", period)
        provider_type = person("childcare_provider_type_group", period.this_year)
        age_group = person("ny_ccap_age_group", period)
        duration = person("ny_ccap_duration_of_care", period)
        durations = duration.possible_values
        days_per_week = person("childcare_days_per_week", period.this_year)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        # 415.9(b): days beyond the weekly maximum are paid at the weekly rate
        # divided by the weekly maximum days.
        excess_days = max_(days_per_week - p.duration.weekly_maximum_days, 0)
        weekly_multiplier = 1 + excess_days / p.duration.weekly_maximum_days

        if p.current_rates_in_effect:
            weekly_rate = p.rates.weekly[county_group][provider_type][age_group]
            daily_rate = p.rates.daily[county_group][provider_type][age_group]
            part_day_rate = p.rates.part_day[county_group][provider_type][age_group]
            rate_per_week = select(
                [
                    duration == durations.WEEKLY,
                    duration == durations.DAILY,
                    duration == durations.PART_DAY,
                    duration == durations.HOURLY,
                ],
                [
                    weekly_rate * weekly_multiplier,
                    daily_rate * days_per_week,
                    part_day_rate * days_per_week,
                    0,
                ],
                default=0,
            )
            return rate_per_week * weeks_per_month

        historical_rate = p.historical_rates[county_group][provider_type][duration][
            age_group
        ]
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        hours_per_week = hours_per_day * days_per_week
        periods_per_week = select(
            [
                duration == durations.WEEKLY,
                duration == durations.DAILY,
                duration == durations.PART_DAY,
                duration == durations.HOURLY,
            ],
            [weekly_multiplier, days_per_week, days_per_week, hours_per_week],
            default=0,
        )
        return historical_rate * periods_per_week * weeks_per_month
