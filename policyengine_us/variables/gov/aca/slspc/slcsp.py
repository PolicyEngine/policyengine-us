from policyengine_us.model_api import *


class slcsp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH

    adds = ["slcsp_person"]

    def formula(tax_unit, period, parameters):
        state_code = tax_unit.household("state_code_str", period)

        # Check if the state uses family tiers
        is_family_tier_state = np.zeros(tax_unit.count, dtype=bool)

        # Check if family tier states parameter exists
        if hasattr(parameters(period).gov.aca, "family_tier_states"):
            try:
                is_ny = state_code == "NY"
                is_vt = state_code == "VT"

                is_ny_family_tier = (
                    is_ny
                    & parameters(period).gov.aca.family_tier_states.states.NY
                )
                is_vt_family_tier = (
                    is_vt
                    & parameters(period).gov.aca.family_tier_states.states.VT
                )

                is_family_tier_state = is_ny_family_tier | is_vt_family_tier
            except AttributeError:
                # Fall back to hardcoded values
                is_family_tier_state = (state_code == "NY") | (
                    state_code == "VT"
                )
        else:
            # If parameter doesn't exist, use hardcoded values for NY and VT
            is_family_tier_state = (state_code == "NY") | (state_code == "VT")

        # For family tier states, use family tier pricing
        base_cost = tax_unit.household("slcsp_age_0", period)
        tier_multiplier = tax_unit("family_tier_multiplier", period)
        family_tier_premium = base_cost * tier_multiplier

        # For age rating states, sum individual premiums
        individual_premium_sum = add(tax_unit, period, ["slcsp_person"])

        # Choose the appropriate method based on state
        return where(
            is_family_tier_state, family_tier_premium, individual_premium_sum
        )
