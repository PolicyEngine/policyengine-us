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

        person = tax_unit.members
        age = person("age", period.this_year)
        dependent_child = (age <= p.slcsp.max_child_age) | (
            person("is_tax_unit_dependent", period.this_year)
            & (age < p.family_tier_dependent_child_age_threshold)
        )
        adult_count = tax_unit("tax_unit_size", period) - tax_unit.sum(dependent_child)
        family_tier_applies = family_category != FamilyTierCategory.INDIVIDUAL_AGE_RATED
        extra_adults = where(family_tier_applies, max_(adult_count - 2, 0), 0)
        return base_multiplier + extra_adults * one_adult
