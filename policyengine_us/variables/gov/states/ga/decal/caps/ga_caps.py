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
        # PDF pages 27, 55
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=69",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps
        person = spm_unit.members
        weekly_to_monthly = WEEKS_IN_YEAR / MONTHS_IN_YEAR

        # CCDF Plan §4.3.3 phrases the Quality Rated bonus as a per-provider
        # add-on.
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
        max_weekly = person("ga_caps_maximum_weekly_benefit", period)

        # CAPS/00-5, 5.4.1 and CAPS/00-7, 7.5: each child in DFCS custody forms a
        # family unit of one and owes no family fee. The SPM unit's expenses split
        # evenly across its children in pre_subsidy_childcare_expenses, which sets
        # each such child's share.
        dfcs_child = person("ga_caps_dfcs_custody_child", period)
        child_expense = person("pre_subsidy_childcare_expenses", period)
        dfcs_payment = spm_unit.sum(
            min_(child_expense, max_weekly * weekly_to_monthly)
            * (1 + bonus_rate)
            * dfcs_child
        )
        dfcs_expenses = spm_unit.sum(child_expense * dfcs_child)

        # The family's own case covers its other eligible children against the rest
        # of the SPM unit's expenses, less the family fee.
        family_eligible = spm_unit("ga_caps_family_eligible", period)
        family_child = (
            person("ga_caps_eligible_child", period)
            & ~person("is_in_foster_care", period)
            & spm_unit.project(family_eligible)
        )
        family_max_weekly = spm_unit.sum(max_weekly * family_child)
        expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        family_expenses = max_(expenses - dfcs_expenses, 0)
        family_base = min_(family_expenses, family_max_weekly * weekly_to_monthly)
        family_fee = spm_unit("ga_caps_family_fee", period)
        family_net = max_(family_base - family_fee, 0)
        # We don't distinguish provider rating per child within the family's case at
        # the moment, so we collapse to one effective bonus rate weighted by each
        # child's maximum weekly benefit.
        weighted_bonus = spm_unit.sum(max_weekly * bonus_rate * family_child)
        effective_bonus_rate = np.divide(
            weighted_bonus,
            family_max_weekly,
            out=np.zeros_like(weighted_bonus),
            where=family_max_weekly > 0,
        )
        return family_net * (1 + effective_bonus_rate) + dfcs_payment
