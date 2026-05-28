from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class medicaid_slcsp_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    definition_period = YEAR
    label = "Medicaid SLCSP family tier category"

    def formula(tax_unit, period, parameters):
        state = tax_unit.household("state_code_str", period)
        family_tier_applies = tax_unit("slcsp_family_tier_applies", period.first_month)

        child_count = tax_unit.sum(
            tax_unit.members("is_medicaid_slcsp_dependent_child", period)
        )
        adult_count = tax_unit("tax_unit_size", period) - child_count

        one_adult_no_children = (adult_count == 1) & (child_count == 0)
        two_plus_adults_no_children = (adult_count >= 2) & (child_count == 0)
        one_adult_with_children = (adult_count == 1) & (child_count > 0)
        two_plus_adults_with_children = (adult_count >= 2) & (child_count > 0)
        ny_child_only = (state == "NY") & (adult_count == 0) & (child_count > 0)

        return select(
            [
                ny_child_only,
                family_tier_applies & one_adult_no_children,
                family_tier_applies & two_plus_adults_no_children,
                family_tier_applies & one_adult_with_children,
                family_tier_applies & two_plus_adults_with_children,
            ],
            [
                FamilyTierCategory.CHILD_ONLY,
                FamilyTierCategory.ONE_ADULT,
                FamilyTierCategory.TWO_ADULTS,
                FamilyTierCategory.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                FamilyTierCategory.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
            ],
            default=FamilyTierCategory.INDIVIDUAL_AGE_RATED,
        )
