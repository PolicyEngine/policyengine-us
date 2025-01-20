from policyengine_us.model_api import *

class slspc_age_adjusted_cost_person(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost adjusted for age"
    unit = USD
    definition_period = MONTH

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        age = person("monthly_age", period)
        base_cost = person.household("slspc_baseline_cost_at_age_0", period)

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