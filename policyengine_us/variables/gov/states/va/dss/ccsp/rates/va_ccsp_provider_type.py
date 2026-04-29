from policyengine_us.model_api import *


class VACCSPProviderType(Enum):
    CENTER = "Center"
    FAMILY_DAY_HOME = "Family Day Home"


class va_ccsp_provider_type(Variable):
    value_type = Enum
    possible_values = VACCSPProviderType
    default_value = VACCSPProviderType.CENTER
    entity = Person
    definition_period = YEAR
    label = "Virginia CCSP provider type"
    defined_for = StateCode.VA
    reference = "https://www.childcare.virginia.gov/home/showpublisheddocument/66667/638981099706730000#page=203"
