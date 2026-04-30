from policyengine_us.model_api import *


class WAWCCCTimeCategory(Enum):
    PART_TIME = "Part Time"
    FULL_TIME = "Full Time"


class wa_wccc_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCTimeCategory
    default_value = WAWCCCTimeCategory.FULL_TIME
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC authorization time category"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0190"
    # We don't track approved-activity hours at the moment; defaults to
    # FULL_TIME but accepts user override for partial-time scenarios.
