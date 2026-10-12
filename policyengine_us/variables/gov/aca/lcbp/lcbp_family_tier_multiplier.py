from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class lcbp_family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA bronze family tier multiplier for premium calculation"
    unit = "/1"
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        family_category = tax_unit("lcbp_family_tier_category", period)
        p = parameters(period).gov.aca.family_tier_ratings
        state_code = tax_unit.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY

        base_multiplier = select(
            [
                family_category == FamilyTierCategory.ONE_ADULT,
                family_category == FamilyTierCategory.TWO_ADULTS,
                family_category
                == FamilyTierCategory.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                family_category
                == FamilyTierCategory.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
                (family_category == FamilyTierCategory.CHILD_ONLY) & in_ny,
            ],
            [
                where(
                    in_ny,
                    p.ny.ONE_ADULT,
                    p.vt.ONE_ADULT,
                ),
                where(
                    in_ny,
                    p.ny.TWO_ADULTS,
                    p.vt.TWO_ADULTS,
                ),
                where(
                    in_ny,
                    p.ny.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                    p.vt.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                ),
                where(
                    in_ny,
                    p.ny.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
                    p.vt.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
                ),
                p.ny.CHILD_ONLY,
            ],
            default=0,
        )

        person = tax_unit.members
        pays_premium = person("pays_aca_premium", period)
        dependent_child = person("is_aca_family_tier_dependent_child", period)
        adult_count = tax_unit.sum(pays_premium & ~dependent_child)
        extra_adults = max_(adult_count - 2, 0)
        one_adult = where(in_ny, p.ny.ONE_ADULT, p.vt.ONE_ADULT)
        age_29_child = person("is_aca_ny_age_29_dependent_child", period)
        age_29_multiplier = where(
            tax_unit.any(age_29_child),
            parameters(period).gov.aca.ny_age_29_dependent_child_tier_multiplier,
            1,
        )
        return base_multiplier * age_29_multiplier + extra_adults * one_adult
