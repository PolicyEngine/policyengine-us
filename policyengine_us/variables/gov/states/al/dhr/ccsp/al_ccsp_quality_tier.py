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
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/Provider-Rates-with-QRIS-Tiers-April-1-2022-b.pdf#page=2"
