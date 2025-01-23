from policyengine_us.model_api import *


class slspc_person(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        age = person("monthly_age", period)
        base_cost = person.household("slspc_age_0", period)


        p = parameters(period).gov.aca.age_curves
        multiplier = select(
            [
                state_code == "AL",
                state_code == "DC",
                state_code == "MA",
                state_code == "MN",
                state_code == "MS",
                state_code == "OR",
                state_code == "UT",
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
        return base_cost * multiplier
