from policyengine_us.model_api import *


class KSCCAPProviderType(Enum):
    CENTER = "Child Care Center"
    LICENSED_HOME = "Licensed Child Care Home"
    OUT_OF_HOME_RELATIVE = "Out-of-Home Relative Care"
    IN_HOME_RELATIVE = "In-Home Relative Care"
    ENHANCED_SPECIAL_CARE = "Enhanced Rate for Special Care"


class ks_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = KSCCAPProviderType
    default_value = KSCCAPProviderType.CENTER
    definition_period = MONTH
    label = "Kansas CCAP child care provider type"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )
