from policyengine_us.model_api import *


class NYCCAPDurationOfCare(Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    PART_DAY = "Part-Day"
    HOURLY = "Hourly"


class ny_ccap_duration_of_care(Variable):
    value_type = Enum
    possible_values = NYCCAPDurationOfCare
    default_value = NYCCAPDurationOfCare.PART_DAY
    entity = Person
    label = "New York CCAP market-rate duration of care"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=5",
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=44",
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=45",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        days_per_week = person("childcare_days_per_week", period.this_year)
        hours_per_week = hours_per_day * days_per_week
        weekly = (hours_per_week >= p.duration.weekly_minimum_hours) & (
            days_per_week <= p.duration.weekly_maximum_days
        )
        daily = (hours_per_day >= p.duration.daily_minimum_hours) & (
            hours_per_day < p.duration.daily_maximum_hours
        )

        if p.current_rates_in_effect:
            # Care at 12+ hours receives a daily base period plus an excess
            # period. The base category is modeled; excess periods are not.
            extended_daily = (hours_per_day >= p.duration.daily_maximum_hours) & ~weekly
            return select(
                [
                    weekly,
                    daily,
                    hours_per_day < p.duration.daily_minimum_hours,
                    extended_daily,
                ],
                [
                    NYCCAPDurationOfCare.WEEKLY,
                    NYCCAPDurationOfCare.DAILY,
                    NYCCAPDurationOfCare.PART_DAY,
                    NYCCAPDurationOfCare.DAILY,
                ],
                default=NYCCAPDurationOfCare.PART_DAY,
            )

        historical_daily = hours_per_day >= p.duration.daily_minimum_hours
        return select(
            [
                weekly,
                historical_daily,
                hours_per_day >= 3,
                hours_per_day < 3,
            ],
            [
                NYCCAPDurationOfCare.WEEKLY,
                NYCCAPDurationOfCare.DAILY,
                NYCCAPDurationOfCare.PART_DAY,
                NYCCAPDurationOfCare.HOURLY,
            ],
            default=NYCCAPDurationOfCare.HOURLY,
        )
