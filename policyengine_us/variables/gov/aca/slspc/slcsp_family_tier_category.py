from policyengine_us.model_api import *


class FamilyTierCategory(Enum):
    INDIVIDUAL_AGE_RATED = "Individual age rated"
    ONE_ADULT = "One_adult"
    TWO_ADULTS = "Two_adults"
    ONE_ADULT_AND_ONE_OR_MORE_CHILDREN = "One_adult_and_one_or_more_children"
    TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN = "Two_adults_and_one_or_more_children"
    CHILD_ONLY = "Child_only"


class slcsp_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    definition_period = MONTH
    label = "ACA family tier category for premium calculation"
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        """
        Determine the family tier category for premium calculation in states
        that use family tiers instead of individual age rating.

        Categories for both NY and VT:
        - One_adult
        - Two_adults
        - One_adult_and_one_or_more_children
        - Two_adults_and_one_or_more_children
        - Child_only (only for NY)
        """
        # Get inputs
        state_code = tax_unit.household("state_code_str", period)

        person = tax_unit.members
        pays_premium = person("pays_aca_premium", period)
        dependent_child = person("is_aca_family_tier_dependent_child", period)
        non_dependent_adult_count = tax_unit.sum(pays_premium & ~dependent_child)
        anchored_child_count = tax_unit.sum(dependent_child)

        under_child_only_age = (
            person("monthly_age", period)
            <= parameters(period).gov.aca.slcsp.max_child_age
        )
        child_only_child = pays_premium & under_child_only_age
        unanchored_adult_count = tax_unit.sum(pays_premium & ~child_only_child)
        unanchored_child_count = tax_unit.sum(child_only_child)
        has_adult_anchor = non_dependent_adult_count > 0
        eligible_adult_count = where(
            has_adult_anchor,
            non_dependent_adult_count,
            unanchored_adult_count,
        )
        eligible_child_count = where(
            has_adult_anchor,
            anchored_child_count,
            unanchored_child_count,
        )

        # Common conditions for both states
        one_adult_no_children = (eligible_adult_count == 1) & (
            eligible_child_count == 0
        )
        two_plus_adults_no_children = (eligible_adult_count >= 2) & (
            eligible_child_count == 0
        )
        one_adult_with_children = (eligible_adult_count == 1) & (
            eligible_child_count > 0
        )
        two_plus_adults_with_children = (eligible_adult_count >= 2) & (
            eligible_child_count > 0
        )

        # NY-specific condition (child-only households)
        ny_child_only = (
            (state_code == "NY")
            & (eligible_adult_count == 0)
            & (eligible_child_count > 0)
        )

        return select(
            [
                # Apply conditions only to family tier states
                ny_child_only,
                one_adult_no_children,
                two_plus_adults_no_children,
                one_adult_with_children,
                two_plus_adults_with_children,
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
