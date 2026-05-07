from policyengine_us.model_api import *


class lcbp_age_curve_amount_person(Variable):
    value_type = float
    entity = Person
    label = "Lowest-cost ACA bronze-plan cost, for people in age curve states"
    unit = USD
    definition_period = MONTH
    defined_for = "pays_aca_premium"

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        age = person("monthly_age", period)
        base_cost = person.household("lcbp_age_0", period)

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
                p.al.calc(age),
                p.dc.calc(age),
                p.ma.calc(age),
                p.mn.calc(age),
                p.ms.calc(age),
                p["or"].calc(age),
                p.ut.calc(age),
            ],
            default=p.default.calc(age),
        )
        age_curve_applies = person.tax_unit("slcsp_age_curve_applies", period)
        return base_cost * multiplier * age_curve_applies
