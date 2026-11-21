from policyengine_us.model_api import *
from policyengine_us.tools.childcare import childcare_hours_for_daily_schedule


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
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter168/055_0168.pdf#page=4"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw
        # 55 Pa. Code § 168.2 is the codified definition (chapter 3042 defines
        # no hours): "Full-time care—Child care of at least 5 hours per day";
        # "Part-time care—Child care of less than 5 hours per day".
        # Unresolved hours retain full-time pricing; attendance and expense
        # rules still determine payment.
        hours_per_day = childcare_hours_for_daily_schedule(person, period)
        return where(
            (hours_per_day == 0) | (hours_per_day >= p.full_time_hours_per_day),
            PACCWTimeCategory.FULL_TIME,
            PACCWTimeCategory.PART_TIME,
        )
