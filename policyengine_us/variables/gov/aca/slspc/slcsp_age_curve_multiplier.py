from policyengine_us.model_api import *


class slcsp_age_curve_multiplier(Variable):
    value_type = float
    entity = Person
    label = "ACA SLCSP age curve multiplier"
    unit = "/1"
    definition_period = MONTH

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        age = person("monthly_age", period)
        p = parameters(period).gov.aca.age_curves

        return select(
            [
                state_code == "AL",
                state_code == "DC",
                state_code == "MA",
                state_code == "MN",
                state_code == "MS",
                state_code == "NY",
                state_code == "OR",
                state_code == "UT",
                state_code == "VT",
            ],
            [
                p.al.calc(age),
                p.dc.calc(age),
                p.ma.calc(age),
                p.mn.calc(age),
                p.ms.calc(age),
                p.ny.calc(age),
                p["or"].calc(age),
                p.ut.calc(age),
                # VT has no age variation: vt is a flat scalar, not an age scale,
                # so it is read directly rather than via .calc(age).
                p.vt,
            ],
            default=p.default.calc(age),
        )
