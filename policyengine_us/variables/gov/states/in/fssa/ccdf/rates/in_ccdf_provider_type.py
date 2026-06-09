from policyengine_us.model_api import *


class INCCDFProviderType(Enum):
    LICENSED_CENTER = "Licensed center"
    LICENSED_HOME = "Licensed home"
    REGISTERED_MINISTRY = "Registered child care ministry"
    EXEMPT_CENTER = "Legally license exempt center"
    ACCREDITED_EXEMPT_CENTER = "Accredited legally license exempt center"
    EXEMPT_HOME = "Legally license exempt home"


class in_ccdf_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = INCCDFProviderType
    default_value = INCCDFProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.IN
    label = "Indiana CCDF provider type"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=37"
    )
