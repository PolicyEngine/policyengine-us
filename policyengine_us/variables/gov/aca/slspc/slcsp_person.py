from policyengine_us.model_api import *


class slcsp_person(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        age = person("monthly_age", period)
        base_cost = person.household("slcsp_age_0", period)

        p = parameters(period).gov.aca.age_curves
        
        # Handle VT separately since it uses a simple value, not a bracket structure
        is_vt = state_code == "VT"
        vt_value = p.vt
        
        # Handle other states with regular bracket structures
        multiplier = select(
            [
                is_vt,
                state_code == "AL",
                state_code == "DC",
                state_code == "MA",
                state_code == "MN",
                state_code == "MS",
                state_code == "NY",
                state_code == "OR",
                state_code == "UT",
            ],
            [
                vt_value,
                p.al.calc(age),
                p.dc.calc(age),
                p.ma.calc(age),
                p.mn.calc(age),
                p.ms.calc(age),
                p.ny.calc(age),
                p["or"].calc(age),
                p.ut.calc(age),
            ],
            default=p.default.calc(age),
        )
        return base_cost * multiplier
