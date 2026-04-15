from policyengine_us.model_api import *


class MECCAPTimeCategory(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    HALF_TIME = "Half Time"
    QUARTER_TIME = "Quarter Time"


class me_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MECCAPTimeCategory
    default_value = MECCAPTimeCategory.PART_TIME
    definition_period = MONTH
    defined_for = StateCode.ME
    label = "Maine CCAP time category"
    reference = (
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=28",
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/July%206%202024%20Market%20Rates_5_0.pdf",
    )

    def formula(person, period, parameters):
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.me.dhhs.ccap.hours
        if p.uses_simplified_time:
            return where(
                hours >= p.full_time_threshold,
                MECCAPTimeCategory.FULL_TIME,
                MECCAPTimeCategory.PART_TIME,
            )
        return select(
            [
                hours >= p.full_time_threshold,
                hours >= p.part_time_threshold,
                hours >= p.half_time_threshold,
            ],
            [
                MECCAPTimeCategory.FULL_TIME,
                MECCAPTimeCategory.PART_TIME,
                MECCAPTimeCategory.HALF_TIME,
            ],
            default=MECCAPTimeCategory.QUARTER_TIME,
        )
