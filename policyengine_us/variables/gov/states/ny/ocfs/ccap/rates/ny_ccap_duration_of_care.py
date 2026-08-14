from policyengine_us.model_api import *


class NYCCAPDurationOfCare(Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    PART_DAY = "Part-Day"


class ny_ccap_duration_of_care(Variable):
    value_type = Enum
    possible_values = NYCCAPDurationOfCare
    default_value = NYCCAPDurationOfCare.PART_DAY
    entity = Person
    label = "New York CCAP market-rate duration of care"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "18 NYCRR 415.9(a)-(d) sets the rate unit. Weekly rates apply at 30 "
        "or more hours of care per week; daily rates apply at six to twelve "
        "hours per day only when weekly care is under 30 hours, because "
        "415.9(b) directs that care of 30 or more hours per week billed "
        "daily is paid at the weekly rate divided by five. Days beyond the "
        "weekly maximum are priced as additional periods in "
        "ny_ccap_market_rate."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=44",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        days_per_week = person("childcare_days_per_week", period.this_year)
        hours_per_week = hours_per_day * days_per_week
        # 415.9(a): the weekly rate applies at or above the weekly minimum
        # hours. Schedules beyond the weekly maximum days remain weekly and
        # earn additional periods rather than switching to a daily rate.
        weekly = hours_per_week >= p.duration.weekly_minimum_hours
        # 415.9(b): daily rates require both the daily hour band and weekly
        # care below the weekly minimum hours.
        daily = (
            (hours_per_day >= p.duration.daily_minimum_hours)
            & (hours_per_day < p.duration.daily_maximum_hours)
            & (hours_per_week < p.duration.weekly_minimum_hours)
        )
        # Care at 12+ hours receives a daily base period plus an excess
        # period. The base category is modeled; excess periods are not.
        extended_daily = (hours_per_day >= p.duration.daily_maximum_hours) & ~weekly
        return select(
            [
                weekly,
                daily,
                extended_daily,
                hours_per_day < p.duration.daily_minimum_hours,
            ],
            [
                NYCCAPDurationOfCare.WEEKLY,
                NYCCAPDurationOfCare.DAILY,
                NYCCAPDurationOfCare.DAILY,
                NYCCAPDurationOfCare.PART_DAY,
            ],
            default=NYCCAPDurationOfCare.PART_DAY,
        )
