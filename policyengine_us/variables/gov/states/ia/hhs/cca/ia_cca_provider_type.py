from policyengine_us.model_api import *


class IACCAProviderType(Enum):
    LICENSED_CENTER = "Licensed Center"
    CHILD_DEVELOPMENT_HOME_AB = "Child Development Home A or B"
    CHILD_DEVELOPMENT_HOME_C = "Child Development Home C"
    CHILD_CARE_HOME_NOT_REGISTERED = "Child Care Home (Not Registered)"
    IN_HOME = "In-Home Provider"


class ia_cca_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = IACCAProviderType
    default_value = IACCAProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Iowa CCA child care provider type"
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=14"
