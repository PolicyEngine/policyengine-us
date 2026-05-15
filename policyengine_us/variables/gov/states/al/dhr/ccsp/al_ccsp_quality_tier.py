from policyengine_us.model_api import *


class ALCCSPQualityTier(Enum):
    BASE = "Base"
    STAR_1 = "1 Star"
    STAR_2 = "2 Star"
    STAR_3 = "3 Star"
    STAR_4 = "4 Star"
    STAR_5 = "5 Star"


class al_ccsp_quality_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = ALCCSPQualityTier
    default_value = ALCCSPQualityTier.BASE
    definition_period = MONTH
    label = "Alabama CCSP provider quality tier"
    defined_for = StateCode.AL
    reference = (
        "Alabama DHR Provider Rate Chart (Base + 1-5 Star)",
        "https://www.alacourt.gov/docs/ALDayCareRates.pdf",
    )
