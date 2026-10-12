from policyengine_us.model_api import *


class KYCCAPProviderType(Enum):
    LICENSED_TYPE_I = "Licensed Type I"
    LICENSED_TYPE_II = "Licensed Type II"
    CERTIFIED = "Certified"
    REGISTERED = "Registered"


class ky_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = KYCCAPProviderType
    default_value = KYCCAPProviderType.LICENSED_TYPE_I
    definition_period = MONTH
    label = "Kentucky CCAP child care provider type"
    defined_for = StateCode.KY
    reference = "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc300kymaxpaymentchart.pdf#page=1"
