from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class slcsp_family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA family tier multiplier for premium calculation"
    unit = "/1"
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        family_category = tax_unit("slcsp_family_tier_category", period)
        p = parameters(period).gov.aca.family_tier_ratings
        state_code = tax_unit.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY

        one_adult = where(in_ny, p.ny.ONE_ADULT, p.vt.ONE_ADULT)
        two_adults = where(in_ny, p.ny.TWO_ADULTS, p.vt.TWO_ADULTS)
        one_adult_with_children = where(
            in_ny,
            p.ny.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
            p.vt.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
        )
        two_adults_with_children = where(
            in_ny,
            p.ny.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
            p.vt.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
        )
        child_only = where(in_ny, p.ny.CHILD_ONLY, 0)

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
        pays_premium = person("pays_aca_premium", period)
        dependent_child = person("is_aca_family_tier_dependent_child", period)
        adult_count = tax_unit.sum(pays_premium & ~dependent_child)
        extra_adults = max_(adult_count - 2, 0)
        age_29_child = person("is_aca_ny_age_29_dependent_child", period)
        age_29_multiplier = where(
            tax_unit.any(age_29_child),
            parameters(period).gov.aca.ny_age_29_dependent_child_tier_multiplier,
            1,
        )
        return base_multiplier * age_29_multiplier + extra_adults * one_adult
