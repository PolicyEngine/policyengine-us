from policyengine_us.model_api import *


class IllinoisCCAPDayCareCategory(Enum):
    LICENSED_DAY_CARE_CENTER = "Licensed Day Care Center"
    LICENSED_EXEMPT_DAY_CARE_CENTER = "Licensed-Exempt Day Care Center"
    LICENSED_DAY_CARE_HOME_OR_LICENSED_GROUP_DAY_CARE_HOME = (
        "Licensed Day Care Home or Licensed Group Day Care Home"
    )
    NON_LICENSED_CARE = "License-Exempt Day Care Home and Relative and Non-Relative Care in the Child's Home"
    NONE = "None"


class il_ccap_day_care_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = IllinoisCCAPDayCareCategory
    default_value = IllinoisCCAPDayCareCategory.NONE
    definition_period = MONTH
    label = "Illinois Child Care Assistance Program (CCAP) day care category"
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=163817"
