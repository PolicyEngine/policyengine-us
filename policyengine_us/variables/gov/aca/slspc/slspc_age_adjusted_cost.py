from policyengine_us.model_api import *

class slspc_age_adjusted_cost(Variable):
    value_type = float
    entity = Household
    label = "Second-lowest ACA silver-plan cost adjusted for age"
    unit = USD
    definition_period = MONTH

    def formula(household, period, parameters):
        state = household("state_code", period).decode_to_str()
        age = household("age", period)
        base_cost = household("slspc_baseline_cost_at_age_0", period)

        # Get age curve based on state
        special_states = ["district_of_columbia", "alabama", "massachusetts", 
                         "minnesota", "mississippi", "oregon", "utah"]
        curve_name = state.lower() if state.lower() in special_states else "default"
        age_curve = parameters.gov.aca.age_curves[curve_name]

        # Find applicable bracket
        brackets = age_curve.brackets
        applicable_bracket = max(
            (b for b in brackets if b.threshold <= age),
            key=lambda b: b.threshold
        )

        return base_cost * applicable_bracket.amount