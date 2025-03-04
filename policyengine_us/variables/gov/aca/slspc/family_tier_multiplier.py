from policyengine_us.model_api import *


class family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA family tier multiplier for premium calculation"
    unit = "/1"
    definition_period = MONTH

    def formula(tax_unit, period, parameters):
        """
        Returns the multiplier for family tier premium calculation in states
        that use family tiers instead of individual age rating.
        """
        state_code = tax_unit.household("state_code_str", period)
        family_category = tax_unit("family_tier_category", period)

        # Default multiplier is 1.0
        result = np.ones(tax_unit.count, dtype=float)

        # Check if the parameter exists before using
        if not hasattr(
            parameters(period).gov.aca, "family_tier_ratings"
        ) or not hasattr(parameters(period).gov.aca, "family_tier_states"):
            return result

        # New York multipliers
        is_ny = state_code == "NY"
        try:
            is_ny_family_tier = (
                is_ny & parameters(period).gov.aca.family_tier_states.states.NY
            )
        except AttributeError:
            # Fall back to hardcoded value if parameter is not structured as expected
            is_ny_family_tier = is_ny

        # Only apply NY multipliers if the family_tier_ratings.ny parameter exists
        if hasattr(parameters(period).gov.aca.family_tier_ratings, "ny"):
            ny_params = parameters(period).gov.aca.family_tier_ratings.ny

            # Apply multipliers for each category
            result = where(
                is_ny_family_tier & (family_category == "one_adult"),
                ny_params.one_adult,
                result,
            )
            result = where(
                is_ny_family_tier & (family_category == "two_adults"),
                ny_params.two_adults,
                result,
            )
            result = where(
                is_ny_family_tier
                & (family_category == "one_adult_and_one_or_more_children"),
                ny_params.one_adult_and_one_or_more_children,
                result,
            )
            result = where(
                is_ny_family_tier
                & (family_category == "two_adults_and_one_or_more_children"),
                ny_params.two_adults_and_one_or_more_children,
                result,
            )
            result = where(
                is_ny_family_tier & (family_category == "child_only"),
                ny_params.child_only,
                result,
            )

        # Vermont multipliers
        is_vt = state_code == "VT"
        try:
            is_vt_family_tier = (
                is_vt & parameters(period).gov.aca.family_tier_states.states.VT
            )
        except AttributeError:
            # Fall back to hardcoded value if parameter is not structured as expected
            is_vt_family_tier = is_vt

        # Only apply VT multipliers if the family_tier_ratings.vt parameter exists
        if hasattr(parameters(period).gov.aca.family_tier_ratings, "vt"):
            vt_params = parameters(period).gov.aca.family_tier_ratings.vt

            # Apply multipliers for each category
            result = where(
                is_vt_family_tier & (family_category == "one_adult"),
                vt_params.one_adult,
                result,
            )
            result = where(
                is_vt_family_tier & (family_category == "two_adults"),
                vt_params.two_adults,
                result,
            )
            result = where(
                is_vt_family_tier
                & (family_category == "one_adult_and_one_or_more_children"),
                vt_params.one_adult_and_one_or_more_children,
                result,
            )
            result = where(
                is_vt_family_tier
                & (family_category == "two_adults_and_one_or_more_children"),
                vt_params.two_adults_and_one_or_more_children,
                result,
            )

        return result
