from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ga.decal.caps.payment.ga_caps_quality_rating import (
    GACAPSQualityRating,
)


class ga_caps(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Georgia CAPS benefit amount"
    definition_period = MONTH
    defined_for = "ga_caps_eligible"
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=55",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=69",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps
        person = spm_unit.members

        max_weekly = person("ga_caps_maximum_weekly_benefit", period)
        published_weekly = person("ga_caps_provider_published_rate", period)
        per_child_weekly = min_(max_weekly, published_weekly)

        total_weekly_base = spm_unit.sum(per_child_weekly)
        base_monthly = total_weekly_base * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)

        family_fee = spm_unit("ga_caps_family_fee", period)
        net_base = max_(base_monthly - family_fee, 0)

        quality_rating = person("ga_caps_quality_rating", period)
        star_count = select(
            [
                quality_rating == GACAPSQualityRating.ONE_STAR,
                quality_rating == GACAPSQualityRating.TWO_STAR,
                quality_rating == GACAPSQualityRating.THREE_STAR,
            ],
            [1, 2, 3],
            default=0,
        )
        bonus_rate = p.quality_rated.bonus_rate.calc(star_count)
        weighted_bonus = spm_unit.sum(per_child_weekly * bonus_rate)
        effective_bonus_rate = where(
            total_weekly_base > 0,
            weighted_bonus / total_weekly_base,
            0,
        )
        return net_base * (1 + effective_bonus_rate)
