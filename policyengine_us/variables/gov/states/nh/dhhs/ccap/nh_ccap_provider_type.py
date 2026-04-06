from policyengine_us.model_api import *


class NHCCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed child care center"
    LICENSED_FAMILY = "Licensed family child care home"
    LICENSE_EXEMPT_IN_HOME = "License-exempt in-home provider"
    LICENSE_EXEMPT_CENTER = "License-exempt child care center"


class nh_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NHCCAPProviderType
    default_value = NHCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.NH
    label = "New Hampshire Child Care Scholarship Program provider type"
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.17"
