from openfisca_us.model_api import *


class ccdf_market_rate(Variable):
    value_type = float
    entity = Person
    label = "CCDF market rate"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        county_cluster = person.household("ccdf_county_cluster", period)
        provider_type_group = person("childcare_provider_type_group", period)
        child_age_group = person("ccdf_age_group", period)
        duration_of_care = person("ccdf_duration_of_care", period)
        durations_of_care = duration_of_care.possible_values
        market_rate_mapping = parameters(period).hhs.ccdf.amount
        rate_per_period = market_rate_mapping[county_cluster][
            provider_type_group
        ][duration_of_care][child_age_group]
        # Multiply by the appropriate factor to get to annual.
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_week = person("childcare_days_per_week", period)
        hours_per_week = hours_per_day * days_per_week
        periods_per_week = select(
            [
                duration_of_care == durations_of_care.WEEKLY,
                duration_of_care == durations_of_care.DAILY,
                duration_of_care == durations_of_care.PART_DAY,
                duration_of_care == durations_of_care.HOURLY,
            ],
            [1, days_per_week, days_per_week, hours_per_week],
        )
        return rate_per_period * periods_per_week * WEEKS_IN_YEAR
