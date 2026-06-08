from policyengine_us.model_api import *


class IDICCPProviderType(Enum):
    CENTER = "Child Care Center"
    FAMILY = "Group or Family Care"


class id_iccp_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = IDICCPProviderType
    default_value = IDICCPProviderType.CENTER
    definition_period = MONTH
    label = "Idaho Child Care Program provider type"
    defined_for = StateCode.ID
    reference = "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS#page=1"
