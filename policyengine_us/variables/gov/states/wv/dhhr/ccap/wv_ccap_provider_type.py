from policyengine_us.model_api import *


class WVCCAPProviderType(Enum):
    FAMILY_HOME = "Family Child Care Home"
    FAMILY_FACILITY = "Family Child Care Facility"
    CENTER = "Child Care Center"
    OUT_OF_SCHOOL_TIME = "Out of School Time"
    INFORMAL_RELATIVE = "Informal/Relative Care"


class wv_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WVCCAPProviderType
    default_value = WVCCAPProviderType.CENTER
    definition_period = MONTH
    label = "West Virginia CCAP child care provider type"
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6831/download?inline#page=1"
