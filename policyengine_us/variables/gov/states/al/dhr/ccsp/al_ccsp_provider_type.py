from policyengine_us.model_api import *


class ALCCSPProviderType(Enum):
    CENTER = "Child Care Center"
    GFDC = "Group Family Day Care Home"
    FDC = "Family Day Care Home"
    INFORMAL = "Informal (License-Exempt) Provider"


class al_ccsp_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = ALCCSPProviderType
    default_value = ALCCSPProviderType.CENTER
    definition_period = MONTH
    label = "Alabama CCSP child care provider type"
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/Provider-Rates-with-QRIS-Tiers-April-1-2022-b.pdf#page=2"
