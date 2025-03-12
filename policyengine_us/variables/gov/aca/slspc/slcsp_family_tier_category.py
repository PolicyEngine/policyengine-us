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

        # Get the maximum child age from parameters
        max_child_age = parameters(period).gov.aca.slcsp.max_child_age

        # For tests, since the age variable is defined yearly but we're running monthly
        # tests, we need to use the direct age values from the input file
        member_ages = tax_unit.members("monthly_age", period)

        # Define adult status using the parameter instead of hardcoded value
        is_adult = member_ages > max_child_age
        adult_count = tax_unit.sum(is_adult)
        # More efficient than recounting: total - adults = children
        child_count = tax_unit("tax_unit_size", period) - adult_count

        # Common conditions for both states
        one_adult_no_children = (adult_count == 1) & (child_count == 0)
        two_plus_adults_no_children = (adult_count >= 2) & (child_count == 0)
        one_adult_with_children = (adult_count == 1) & (child_count > 0)
        two_plus_adults_with_children = (adult_count >= 2) & (child_count > 0)

        # NY-specific condition (child-only households)
        ny_child_only = (
            (state_code == "NY") & (adult_count == 0) & (child_count > 0)
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
