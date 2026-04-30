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

        return select(
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
