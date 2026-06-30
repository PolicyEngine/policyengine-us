from policyengine_us.model_api import *


class OHCCAPQualityTier(Enum):
    GOLD = "Gold (5 stars)"
    SILVER = "Silver (4 stars)"
    BRONZE = "Bronze (3 stars)"
    NONE = "Not rated"


class oh_ccap_quality_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = OHCCAPQualityTier
    default_value = OHCCAPQualityTier.NONE
    definition_period = MONTH
    label = "Ohio CCAP provider Step Up To Quality tier"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10"
