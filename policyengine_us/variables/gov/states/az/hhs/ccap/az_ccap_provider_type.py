from policyengine_us.model_api import *


class AZCCAPProviderType(Enum):
    CENTER = "Child care center"
    GROUP_HOME = "Group home"
    CERTIFIED_FAMILY = "Certified family home or certified in-home provider"
    RELATIVE = "Non-certified relative provider"


class az_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = AZCCAPProviderType
    default_value = AZCCAPProviderType.CENTER
    definition_period = MONTH
    label = "Arizona Child Care Assistance Program provider type"
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf#page=1"
