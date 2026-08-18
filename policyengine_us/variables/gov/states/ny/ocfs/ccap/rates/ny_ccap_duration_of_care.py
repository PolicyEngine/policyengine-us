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
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "18 NYCRR 415.9(a)-(c) sets the base rate unit. The weekly rate is a "
        "full-time slot: at least the weekly minimum hours over no more than "
        "the weekly maximum days, at or above the daily minimum hours. Below "
        "the daily minimum hours 415.9(c) makes the part-day rate mandatory "
        "whatever the weekly total. Everything else at or above the daily "
        "minimum takes the daily rate. Days past the weekly maximum and days at or "
        "above the daily maximum hours earn additional periods in "
        "ny_ccap_market_rate rather than changing this base category."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=44",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.duration
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_week = person("childcare_days_per_week", period)
        # 415.9(a) measures the weekly threshold over five or fewer days, so
        # days beyond the weekly maximum do not help a schedule reach it.
        core_weekly_hours = hours_per_day * min_(days_per_week, p.weekly_maximum_days)
        weekly = (core_weekly_hours >= p.weekly_minimum_hours) & (
            hours_per_day >= p.daily_minimum_hours
        )
        daily = ~weekly & (hours_per_day >= p.daily_minimum_hours)
        return select(
            [weekly, daily],
            [NYCCAPDurationOfCare.WEEKLY, NYCCAPDurationOfCare.DAILY],
            default=NYCCAPDurationOfCare.PART_DAY,
        )
