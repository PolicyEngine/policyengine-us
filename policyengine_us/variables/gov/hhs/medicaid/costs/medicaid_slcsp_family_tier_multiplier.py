from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class medicaid_slcsp_family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid SLCSP family tier multiplier"
    unit = "/1"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        family_category = tax_unit("medicaid_slcsp_family_tier_category", period)
        p = parameters(period).gov.aca
        state_code = tax_unit.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY

        ratings = p.family_tier_ratings
        one_adult = where(in_ny, ratings.ny.ONE_ADULT, ratings.vt.ONE_ADULT)
        two_adults = where(in_ny, ratings.ny.TWO_ADULTS, ratings.vt.TWO_ADULTS)
        one_adult_with_children = where(
            in_ny,
            ratings.ny.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
            ratings.vt.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
        )
        two_adults_with_children = where(
            in_ny,
            ratings.ny.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
            ratings.vt.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
        )
        child_only = where(in_ny, ratings.ny.CHILD_ONLY, 0)

        base_multiplier = select(
            [
                family_category == FamilyTierCategory.ONE_ADULT,
                family_category == FamilyTierCategory.TWO_ADULTS,
                family_category
                == FamilyTierCategory.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                family_category
                == FamilyTierCategory.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
                family_category == FamilyTierCategory.CHILD_ONLY,
            ],
            [
                one_adult,
                two_adults,
                one_adult_with_children,
                two_adults_with_children,
                child_only,
            ],
            default=0,
        )

        members = tax_unit.members
        medicaid_enrolled = members("medicaid_enrolled", period)
        medicaid_dependent_child = members("is_medicaid_slcsp_dependent_child", period)
        child_count = tax_unit.sum(medicaid_enrolled & medicaid_dependent_child)
        adult_count = tax_unit.sum(medicaid_enrolled & ~medicaid_dependent_child)
        family_tier_applies = family_category != FamilyTierCategory.INDIVIDUAL_AGE_RATED
        extra_adults = where(family_tier_applies, max_(adult_count - 2, 0), 0)
        # New York applies a premium loading when the unit covers a tax dependent
        # aged 26-29 (mirrors slcsp_family_tier_multiplier, minus the
        # pays_aca_premium gate that is false for Medicaid enrollees).
        member_age = members("age", period)
        member_is_dependent = members("is_tax_unit_dependent", period)
        member_in_ny = (
            members.household("state_code", period) == state_code.possible_values.NY
        )
        ny_age_29_child = (
            medicaid_enrolled
            & member_in_ny
            & member_is_dependent
            & (member_age >= p.family_tier_dependent_child_age_threshold)
            & (member_age < p.ny_age_29_dependent_child_age_threshold)
        )
        age_29_multiplier = where(
            tax_unit.any(ny_age_29_child),
            p.ny_age_29_dependent_child_tier_multiplier,
            1,
        )
        return base_multiplier * age_29_multiplier + extra_adults * one_adult
