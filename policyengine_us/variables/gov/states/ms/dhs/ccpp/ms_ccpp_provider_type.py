from policyengine_us.model_api import *


class MSCCPPProviderType(Enum):
    CENTER = "Licensed child care center"
    FAMILY_HOME = "Registered family child care home"


class ms_ccpp_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MSCCPPProviderType
    default_value = MSCCPPProviderType.CENTER
    definition_period = MONTH
    label = "Mississippi CCPP child care provider type"
    defined_for = StateCode.MS
    # In-home care is special-needs-only and is paid the home-based special-needs
    # rate, so there is no separate in-home provider type; route in-home and
    # special-needs children through FAMILY_HOME (or CENTER) and the special-needs
    # rate set.
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=56"
