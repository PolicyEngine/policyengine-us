from policyengine_us.model_api import *


class SCCCAPProviderType(Enum):
    CENTER = "Child Care Center"
    EXEMPT_CENTER = "Exempt/Waivered Center"
    GROUP_HOME = "Group Child Care Home"
    LICENSED_FAMILY_HOME = "Licensed Family Child Care Home"
    REGISTERED_FAMILY_HOME = "Registered Family Child Care Home"
    FFN = "Family, Friend, and Neighbor"


class sc_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = SCCCAPProviderType
    default_value = SCCCAPProviderType.CENTER
    definition_period = MONTH
    label = "South Carolina CCAP child care provider type"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=1"
