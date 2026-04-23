from policyengine_us.model_api import *


class VTCCFAPProviderType(Enum):
    LICENSED_CENTER = "Licensed Center"
    REGISTERED_HOME = "Registered Family Child Care Home"


class vt_ccfap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = VTCCFAPProviderType
    default_value = VTCCFAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP provider type"
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-State-Rates.pdf"
