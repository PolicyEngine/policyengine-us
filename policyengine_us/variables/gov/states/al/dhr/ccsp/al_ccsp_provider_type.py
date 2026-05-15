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
    reference = (
        "Alabama DHR Provider Rate Chart",
        "https://www.alacourt.gov/docs/ALDayCareRates.pdf#page=2",
    )
