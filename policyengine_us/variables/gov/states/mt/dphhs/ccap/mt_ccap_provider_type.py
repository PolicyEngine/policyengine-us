from policyengine_us.model_api import *


class MTCCAPProviderType(Enum):
    CENTER = "Child Care Center"
    GROUP_HOME = "Group Home"
    FAMILY_HOME = "Family Home"
    FFN = "Family, Friend & Neighbor"
    RELATIVE_EXEMPT = "Relative Care Exempt"
    SCHOOL_AGE_PROVIDER = "School Age Provider"


class mt_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MTCCAPProviderType
    default_value = MTCCAPProviderType.CENTER
    definition_period = MONTH
    defined_for = StateCode.MT
    label = "Montana Best Beginnings Child Care Scholarship provider type"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.205"
