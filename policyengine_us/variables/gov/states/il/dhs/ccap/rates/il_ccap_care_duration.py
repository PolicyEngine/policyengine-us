from policyengine_us.model_api import *


class ILCCAPCareDuration(Enum):
    PART_DAY = "Part day"
    FULL_DAY = "Full day"
    FULL_PLUS_PART = "Full day plus part day"
    TWO_FULL_DAYS = "Two full days"
    NONE = "No care"


class il_ccap_care_duration(Variable):
    value_type = Enum
    entity = Person
    possible_values = ILCCAPCareDuration
    default_value = ILCCAPCareDuration.NONE
    definition_period = MONTH
    label = "Illinois CCAP daily care duration"
    defined_for = StateCode.IL
    reference = "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.rates.duration
        hours = person("childcare_hours_per_day", period.this_year)
        return select(
            [
                hours <= 0,
                (hours > 0) & (hours < p.part_day_hours_limit),
                (hours >= p.part_day_hours_limit) & (hours <= p.full_day_hours_limit),
                (hours > p.full_day_hours_limit) & (hours < p.extended_day_hours_limit),
                (hours >= p.extended_day_hours_limit)
                & (hours <= p.maximum_daily_hours),
                hours > p.maximum_daily_hours,
            ],
            [
                ILCCAPCareDuration.NONE,
                ILCCAPCareDuration.PART_DAY,
                ILCCAPCareDuration.FULL_DAY,
                ILCCAPCareDuration.FULL_PLUS_PART,
                ILCCAPCareDuration.TWO_FULL_DAYS,
                ILCCAPCareDuration.TWO_FULL_DAYS,
            ],
            default=ILCCAPCareDuration.NONE,
        )
