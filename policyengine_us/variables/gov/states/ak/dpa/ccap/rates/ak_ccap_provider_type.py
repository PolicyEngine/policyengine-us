from policyengine_us.model_api import *


class AKCCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed or military child care center"
    LICENSED_GROUP_HOME = "Licensed group home"
    LICENSED_HOME = "Licensed or military family home"
    APPROVED_RELATIVE_IN_HOME = "Approved relative or in-home care"


class ak_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = AKCCAPProviderType
    default_value = AKCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Alaska CCAP child care provider type"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"
