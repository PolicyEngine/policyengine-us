from policyengine_us.model_api import *


class NDCCAPProviderType(Enum):
    CENTER = "Center"
    LICENSED_FAMILY = "Licensed family or group"
    SELF_DECLARED_TRIBAL = "Self-declared or tribal"
    APPROVED_RELATIVE = "Approved relative"


class nd_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NDCCAPProviderType
    default_value = NDCCAPProviderType.CENTER
    definition_period = MONTH
    label = "North Dakota CCAP child care provider type"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"
