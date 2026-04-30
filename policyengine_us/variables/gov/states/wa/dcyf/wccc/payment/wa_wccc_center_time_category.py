from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wa.dcyf.wccc.payment.wa_wccc_time_category import (
    WAWCCCTimeCategory,
)


class WAWCCCCenterTimeCategory(Enum):
    HALF_DAY = "Half Day"
    FULL_DAY = "Full Day"


class wa_wccc_center_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCCenterTimeCategory
    default_value = WAWCCCCenterTimeCategory.FULL_DAY
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC center rate time category"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200"

    def formula(person, period, parameters):
        time_category = person("wa_wccc_time_category", period)
        return where(
            time_category == WAWCCCTimeCategory.FULL_TIME,
            WAWCCCCenterTimeCategory.FULL_DAY,
            WAWCCCCenterTimeCategory.HALF_DAY,
        )
