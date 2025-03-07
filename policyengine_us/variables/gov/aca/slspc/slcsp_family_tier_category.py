from policyengine_us.model_api import *


class FamilyTierCategory(Enum):
    INDIVIDUAL_AGE_RATED = "individual_age_rated"
    ONE_ADULT = "one_adult"
    TWO_ADULTS = "two_adults"
    ONE_ADULT_AND_ONE_OR_MORE_CHILDREN = "one_adult_and_one_or_more_children"
    TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN = "two_adults_and_one_or_more_children"
    CHILD_ONLY = "child_only"


class slcsp_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    definition_period = MONTH
    label = "ACA family tier category for premium calculation"

    def formula(tax_unit, period, parameters):
        """
        Determine the family tier category for premium calculation in states
        that use family tiers instead of individual age rating.

        Categories for both NY and VT:
        - one_adult
        - two_adults
        - one_adult_and_one_or_more_children
        - two_adults_and_one_or_more_children
        - child_only (only for NY)
        """
        # Get inputs
        state_code = tax_unit.household("state_code_str", period)

        # For tests, since the age variable is defined yearly but we're running monthly
        # tests, we need to use the direct age values from the input file
        member_ages = tax_unit.members("monthly_age", period)

        # Define adult status (age 20 or above)
        is_adult = member_ages >= 20
        adult_count = tax_unit.sum(is_adult)
        # More efficient than recounting: total - adults = children
        child_count = tax_unit.count - adult_count

        # Create state masks once
        ny_mask = state_code == "NY"
        vt_mask = state_code == "VT"

        # Create a mask for states that use family tiers (NY or VT)
        family_tier_state = ny_mask | vt_mask

        # Only calculate conditions for relevant states to improve performance
        if not np.any(family_tier_state):
            # No NY or VT households, return default value for all
            return np.full(
                tax_unit.count, FamilyTierCategory.INDIVIDUAL_AGE_RATED
            )

        # Common conditions for both states
        one_adult_no_children = (adult_count == 1) & (child_count == 0)
        two_plus_adults_no_children = (adult_count >= 2) & (child_count == 0)
        one_adult_with_children = (adult_count == 1) & (child_count > 0)
        two_plus_adults_with_children = (adult_count >= 2) & (child_count > 0)

        # NY-specific condition (child-only households)
        ny_child_only = ny_mask & (adult_count == 0) & (child_count > 0)

        return select(
            [
                # Apply conditions only to family tier states
                ny_child_only,
                family_tier_state & one_adult_no_children,
                family_tier_state & two_plus_adults_no_children,
                family_tier_state & one_adult_with_children,
                family_tier_state & two_plus_adults_with_children,
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
