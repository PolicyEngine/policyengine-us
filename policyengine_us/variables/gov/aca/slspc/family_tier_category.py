from policyengine_us.model_api import *


class family_tier_category(Variable):
    value_type = str
    entity = TaxUnit
    label = "ACA family tier category for premium calculation"
    definition_period = MONTH

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
        member_ages = tax_unit.members("age", period.this_year)

        # Define adult status (age 20 or above)
        is_adult = member_ages >= 20
        adult_count = tax_unit.sum(is_adult)
        child_count = tax_unit.sum(~is_adult)

        # Initialize with default category
        result = np.full(tax_unit.count, "individual_age_rated", dtype=object)

        # NY rules
        ny_mask = state_code == "NY"
        result = np.where(
            ny_mask & (adult_count == 0) & (child_count > 0),
            "child_only",
            result,
        )
        result = np.where(
            ny_mask & (adult_count == 1) & (child_count == 0),
            "one_adult",
            result,
        )
        result = np.where(
            ny_mask & (adult_count >= 2) & (child_count == 0),
            "two_adults",
            result,
        )
        result = np.where(
            ny_mask & (adult_count == 1) & (child_count > 0),
            "one_adult_and_one_or_more_children",
            result,
        )
        result = np.where(
            ny_mask & (adult_count >= 2) & (child_count > 0),
            "two_adults_and_one_or_more_children",
            result,
        )

        # VT rules
        vt_mask = state_code == "VT"
        result = np.where(
            vt_mask & (adult_count == 1) & (child_count == 0),
            "one_adult",
            result,
        )
        result = np.where(
            vt_mask & (adult_count >= 2) & (child_count == 0),
            "two_adults",
            result,
        )
        result = np.where(
            vt_mask & (adult_count == 1) & (child_count > 0),
            "one_adult_and_one_or_more_children",
            result,
        )
        result = np.where(
            vt_mask & (adult_count >= 2) & (child_count > 0),
            "two_adults_and_one_or_more_children",
            result,
        )

        return result
