from policyengine_us.model_api import *


class PACCWTimeCategory(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"


class pa_ccw_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = PACCWTimeCategory
    default_value = PACCWTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Pennsylvania CCW time category"
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=4"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        return where(
            hours_per_day >= p.full_time_hours_per_day,
            PACCWTimeCategory.FULL_TIME,
            PACCWTimeCategory.PART_TIME,
        )
