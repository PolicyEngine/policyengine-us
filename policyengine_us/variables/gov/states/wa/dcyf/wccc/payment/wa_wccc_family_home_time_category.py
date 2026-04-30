from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wa.dcyf.wccc.payment.wa_wccc_time_category import (
    WAWCCCTimeCategory,
)


class WAWCCCFamilyHomeTimeCategory(Enum):
    HALF_DAY = "Half Day"
    PARTIAL_DAY = "Partial Day"
    FULL_DAY = "Full Day"


class wa_wccc_family_home_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCFamilyHomeTimeCategory
    default_value = WAWCCCFamilyHomeTimeCategory.FULL_DAY
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC family home rate time category"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205"

    def formula(person, period, parameters):
        time_category = person("wa_wccc_time_category", period)
        return where(
            time_category == WAWCCCTimeCategory.FULL_TIME,
            WAWCCCFamilyHomeTimeCategory.FULL_DAY,
            WAWCCCFamilyHomeTimeCategory.HALF_DAY,
        )
