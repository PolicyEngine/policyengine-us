from policyengine_us.model_api import *


class DEPOCProviderType(Enum):
    FAMILY_HOME = "Family Home"
    CENTER = "Center"


class de_poc_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = DEPOCProviderType
    default_value = DEPOCProviderType.CENTER
    definition_period = MONTH
    label = "Delaware Purchase of Care child care provider type"
    defined_for = StateCode.DE
    reference = "https://dhss.delaware.gov/dss/childcr/"
