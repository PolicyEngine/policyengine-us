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
        sum_max_weekly = spm_unit.sum(max_weekly)
        sum_max_monthly = sum_max_weekly * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)

        expenses_monthly = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        base_monthly = min_(expenses_monthly, sum_max_monthly)

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
        weighted_bonus = spm_unit.sum(max_weekly * bonus_rate)
        effective_bonus_rate = where(
            sum_max_weekly > 0,
            weighted_bonus / sum_max_weekly,
            0,
        )
        return net_base * (1 + effective_bonus_rate)
