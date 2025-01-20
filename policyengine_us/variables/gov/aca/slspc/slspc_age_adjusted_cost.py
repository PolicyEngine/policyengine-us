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
        base_cost = person.household("slspc_baseline_cost", period)

        # Get age curve based on state
        special_states = [
            "district_of_columbia",
            "alabama",
            "massachusetts",
            "minnesota",
            "mississippi",
            "oregon",
            "utah",
        ]
        curve_name = (
            state.lower() if state.lower() in special_states else "default"
        )
        age_curve = parameters.gov.aca.age_curves[curve_name]

        # Find applicable bracket
        brackets = age_curve.brackets
        applicable_bracket = max(
            (b for b in brackets if b.threshold <= age),
            key=lambda b: b.threshold,
        )

        p = parameters(period).gov.aca.age_curved
        applicable_rate = select(
            [
                state_code == "AL",
                state_code == "DC",
                state_code == "MA",
                state_code == "MN",
                state_code == "MS",
                state_code == "OR",
                state == "UT",
            ],
            [
                p.alabama.calc(age),
                p.district_of_columbia.calc(age),
                p.massachusetts.calc(age),
                p.minnesota.calc(age),
                p.mississippi.calc(age),
                p.oregon.calc(age),
                p.utah.calc(age),
            ],
            default=p.default.calc(age),
        )
        return base_cost * applicable_rate
