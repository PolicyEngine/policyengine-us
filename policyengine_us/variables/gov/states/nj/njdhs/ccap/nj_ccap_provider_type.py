from policyengine_us.model_api import *


class NJCCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed Center"
    REGISTERED_FAMILY = "Registered Family"
    APPROVED_HOME = "Approved Home"
    ACA_SUMMER_CAMP = "ACA Summer Camp"


class nj_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NJCCAPProviderType
    default_value = NJCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "New Jersey CCAP child care provider type"
    defined_for = StateCode.NJ
    reference = "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-15-5-2"
