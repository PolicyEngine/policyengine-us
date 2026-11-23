from policyengine_us.model_api import *


class COCCAPQualityTier(Enum):
    TIER_1_2 = "Colorado Shines level 1 or 2"
    TIER_3 = "Colorado Shines level 3"
    TIER_4_5 = "Colorado Shines level 4 or 5"


class co_ccap_quality_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = COCCAPQualityTier
    default_value = COCCAPQualityTier.TIER_1_2
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program rate tier of the child's provider"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130, PDF page 118: tiered rates by quality level.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=118",
        "https://drive.google.com/file/d/1wK5dCjkW_uqj06tTd0af9-fC6gAfGu5v/view",
    )

    def formula(person, period, parameters):
        # Every licensed provider holds at least level 1, so an unrated
        # provider (rating 0) takes the Tier 1 & Tier 2 rates.
        rating = person("co_quality_rating_of_child_care_facility", period.this_year)
        return select(
            [rating >= 4, rating == 3],
            [COCCAPQualityTier.TIER_4_5, COCCAPQualityTier.TIER_3],
            default=COCCAPQualityTier.TIER_1_2,
        )
