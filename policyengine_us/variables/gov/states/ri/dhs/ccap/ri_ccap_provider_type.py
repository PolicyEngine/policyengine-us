from policyengine_us.model_api import *


class RICCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed Center"
    LICENSED_FAMILY = "Licensed Family"
    LICENSE_EXEMPT = "License Exempt"


class ri_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPProviderType
    default_value = RICCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Rhode Island CCAP child care provider type"
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.7.1"
