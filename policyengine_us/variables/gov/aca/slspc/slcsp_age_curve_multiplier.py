from policyengine_us.model_api import *


class slcsp_age_curve_multiplier(Variable):
    value_type = float
    entity = Person
    label = "ACA SLCSP age curve multiplier"
    unit = "/1"
    definition_period = MONTH
    reference = (
        "https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/downloads/2017-state-specific-age-curve-variations-8-9-2013.pdf#page=1",
        "https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/downloads/statespecagecrv053117.pdf#page=1",
    )
    documentation = (
        "Historical federal child factors retain the 2018 premium normalization. "
        "New Jersey's historical curve preserves the age-40 benchmark premium."
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        age = person("monthly_age", period)
        p = parameters(period).gov.aca.age_curves

        anchor_age = np.full_like(age, 40)
        new_jersey = p.nj.calc(age) / p.nj.calc(anchor_age) * p.default.calc(anchor_age)
        return select(
            [
                state_code == "AL",
                state_code == "DC",
                state_code == "MA",
                state_code == "MN",
                state_code == "MS",
                (state_code == "NJ") & p.nj_in_effect,
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
                new_jersey,
                p.ny.calc(age),
                p["or"].calc(age),
                p.ut.calc(age),
                # VT has no age variation: vt is a flat scalar, not an age scale,
                # so it is read directly rather than via .calc(age).
                p.vt,
            ],
            default=p.default.calc(age),
        )
