from policyengine_us.model_api import *


class CCDFDurationOfCare(Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    PART_DAY = "Part-Day"
    HOURLY = "Hourly"


class ccdf_duration_of_care(Variable):
    value_type = Enum
    possible_values = CCDFDurationOfCare
    default_value = CCDFDurationOfCare.WEEKLY
    entity = Person
    label = "Child care duration of care"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf#page=5"

    def formula(person, period):
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_week = person("childcare_days_per_week", period)
        hours_per_week = hours_per_day * days_per_week
        return select(
            [
                hours_per_week >= 30,
                hours_per_day >= 6,
                hours_per_day >= 3,
                True,
            ],
            [
                CCDFDurationOfCare.WEEKLY,
                CCDFDurationOfCare.DAILY,
                CCDFDurationOfCare.PART_DAY,
                CCDFDurationOfCare.HOURLY,
            ],
        )
