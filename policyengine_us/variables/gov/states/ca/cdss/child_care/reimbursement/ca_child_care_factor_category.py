from policyengine_us.model_api import *


class CaChildCareFactorCategory(Enum):
    STANDARD = "Standard Rate Ceilings"
    EVENING_AND_WEEKEND_I = (
        r"Evening/Weekend Care Rate Ceilings (50% or more of time)"
    )
    EVENING_AND_WEEKEND_II = r"Evening/Weekend Care Rate Ceilings (at least 10% but less than 50% of time)"
    EXCEPTIONAL_NEEDS = "Exceptional Needs Care Rate Ceilings"
    SEVERELY_DISABLED = "Severely Disabled Care Rate Ceilings"


class ca_child_care_factor_category(Variable):
    value_type = Enum
    possible_values = CaChildCareFactorCategory
    default_value = CaChildCareFactorCategory.STANDARD
    entity = Person
    label = "California CalWORKs Child Care factor category"
    definition_period = YEAR
    defined_for = StateCode.CA
