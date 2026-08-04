from policyengine_us.model_api import *


class WVCCAPQualityTier(Enum):
    TIER_I = "Tier I"
    TIER_II = "Tier II"
    TIER_III = "Tier III"


class wv_ccap_quality_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = WVCCAPQualityTier
    default_value = WVCCAPQualityTier.TIER_I
    definition_period = MONTH
    label = "West Virginia CCAP provider quality tier"
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6831/download?inline#page=1"
