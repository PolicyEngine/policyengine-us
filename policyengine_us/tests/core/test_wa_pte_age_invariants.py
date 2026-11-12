"""Check Washington exemption age and pathway invariants in collection years.

A claimant aged 61 on December 31 of the filing year reaches 62 by the end
of the following collection year. Each generated claimant appears at their
drawn age, at an older age, below the age threshold, and with disability
retirement. One simulation evaluates those arrangements in every boundary
year, sharing the unreformed system without copying its parameter tree.

The properties compare those arrangements, including fractional age inputs.
They check that only claimants aged at least 61 and below 62 lose categorical
eligibility from 2020 relative to the previous age parameter, and only when
no disability or veteran pathway applies. Separate YAML cases check the
worked households and exemption amounts.

References:
- RCW 84.36.381(3):
  https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381
- 2008 c 6 section 706:
  https://lawfilesext.leg.wa.gov/biennium/2007-08/Pdf/Bills/Session%20Laws/House/3104-S2.SL.pdf#page=85
- 2015 3rd sp.s. c 30 sections 2 and 4:
  https://lawfilesext.leg.wa.gov/biennium/2015-16/Pdf/Bills/Session%20Laws/Senate/5186-S.SL.pdf#page=3
- 2019 c 453 sections 1 and 9:
  https://lawfilesext.leg.wa.gov/biennium/2019-20/Pdf/Bills/Session%20Laws/Senate/5160-S.SL.pdf#page=3
- 2025 c 200 sections 1 and 3:
  https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Session%20Laws/House/1106.SL.pdf#page=3
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

YEARS = (2008, 2015, 2016, 2019, 2020, 2026, 2027)
DRAWN, OLDER, YOUNGER, DISABILITY = range(4)
VARIANTS = (DRAWN, OLDER, YOUNGER, DISABILITY)
# Collection-year veteran requirements, independent of model parameters.
RATING_THRESHOLDS = {
    2008: None,
    2015: None,
    2016: 1,
    2019: 1,
    2020: 0.8,
    2026: 0.8,
    2027: 0.4,
}


def claimant(age=45, *, state="WA", age_increase=1, **inputs):
    return {
        "state": state,
        "age_increase": age_increase,
        "age": age,
        "is_veteran": False,
        "wa_pte_retired_due_to_disability": False,
        "wa_pte_wholly_service_connected_disability": False,
        "wa_pte_receives_va_disability_compensation": False,
        "wa_pte_va_service_connected_rating": 0,
        "wa_pte_va_total_disability_rating": False,
        **inputs,
    }


@st.composite
def claimants(draw):
    return claimant(
        age=draw(
            st.one_of(
                st.sampled_from([60, 60.75, 61, 61.25, 61.75, 62, 62.25]),
                st.integers(0, 400).map(lambda quarters: quarters / 4),
            )
        ),
        state=draw(st.sampled_from(["WA", "OR"])),
        age_increase=draw(st.integers(0, 80).map(lambda quarters: quarters / 4)),
        is_veteran=draw(st.booleans()),
        wa_pte_retired_due_to_disability=draw(st.booleans()),
        wa_pte_wholly_service_connected_disability=draw(st.booleans()),
        wa_pte_receives_va_disability_compensation=draw(st.booleans()),
        wa_pte_va_service_connected_rating=draw(
            st.sampled_from([0, 0.39, 0.4, 0.79, 0.8, 0.99, 1])
        ),
        wa_pte_va_total_disability_rating=draw(st.booleans()),
    )


def _situation(cases):
    people, tax_units, households = {}, {}, {}
    for index, case in enumerate(cases):
        for variant in VARIANTS:
            name = f"person_{index}_{variant}"
            inputs = {
                key: value
                for key, value in case.items()
                if key not in ("state", "age_increase")
            }
            if variant == OLDER:
                inputs["age"] += case["age_increase"]
            elif variant == YOUNGER:
                inputs["age"] = 0
            elif variant == DISABILITY:
                inputs["wa_pte_retired_due_to_disability"] = True
            inputs.update(
                is_tax_unit_head=True,
                is_tax_unit_spouse=False,
                is_tax_unit_dependent=False,
                real_estate_taxes=5_000,
            )
            people[name] = {
                variable: {year: value for year in YEARS}
                for variable, value in inputs.items()
            }
            tax_units[name] = {
                "members": [name],
                "tax_unit_is_joint": {year: False for year in YEARS},
                "wa_pte_income_eligible": {year: True for year in YEARS},
            }
            households[name] = {
                "members": [name],
                "state_code": {year: case["state"] for year in YEARS},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def _non_age_pathway(case, year):
    if case["state"] != "WA":
        return False
    if case["wa_pte_retired_due_to_disability"]:
        return True
    if not case["is_veteran"]:
        return False
    threshold = RATING_THRESHOLDS[year]
    if threshold is None:
        return case["wa_pte_wholly_service_connected_disability"]
    return case["wa_pte_receives_va_disability_compensation"] and (
        case["wa_pte_va_total_disability_rating"]
        or case["wa_pte_va_service_connected_rating"] >= threshold
    )


ANCHORS = [
    claimant(age=61),
    claimant(age=61.75),
    claimant(age=62),
    claimant(age=61, wa_pte_retired_due_to_disability=True),
    claimant(age=61, state="OR"),
    claimant(is_veteran=True, wa_pte_wholly_service_connected_disability=True),
    *[
        claimant(
            is_veteran=True,
            wa_pte_receives_va_disability_compensation=True,
            wa_pte_va_service_connected_rating=rating,
        )
        for rating in (0.39, 0.4, 0.79, 0.8, 0.99, 1)
    ],
    claimant(
        is_veteran=True,
        wa_pte_receives_va_disability_compensation=True,
        wa_pte_va_total_disability_rating=True,
    ),
    claimant(is_veteran=True, wa_pte_va_total_disability_rating=True),
    claimant(
        wa_pte_receives_va_disability_compensation=True,
        wa_pte_va_service_connected_rating=1,
        wa_pte_va_total_disability_rating=True,
    ),
]


@settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(cases=ANCHORS)
@given(cases=st.lists(claimants(), min_size=1, max_size=12))
def test_wa_pte_collection_year_age_invariants(cases):
    simulation = Simulation(situation=_situation(cases), tax_benefit_system=SYSTEM)
    ages = np.asarray([case["age"] for case in cases])
    in_wa = np.asarray([case["state"] == "WA" for case in cases])
    for year in YEARS:
        eligible = np.asarray(
            simulation.calculate("wa_pte_categorical_eligible", year), dtype=bool
        ).reshape(-1, len(VARIANTS))
        alternative = np.asarray([_non_age_pathway(case, year) for case in cases])
        # Holding every pathway input fixed removes age as the cause.
        np.testing.assert_array_equal(eligible[:, YOUNGER], alternative)
        # Prior December 31 age = collection-year age - 1; 61 + 1 = 62.
        np.testing.assert_array_equal(
            eligible[:, DRAWN], alternative | (in_wa & (ages - 1 >= 61))
        )
        assert np.all(eligible[:, OLDER] >= eligible[:, DRAWN])
        np.testing.assert_array_equal(eligible[:, DISABILITY], in_wa)
        # The previous parameter used 62 before 2020 and 61 from 2020.
        previous = alternative | (in_wa & (ages >= (62 if year < 2020 else 61)))
        intended_loss = (
            (year >= 2020) & in_wa & (ages >= 61) & (ages < 62) & ~alternative
        )
        np.testing.assert_array_equal(previous & ~eligible[:, DRAWN], intended_loss)
        assert not np.any(eligible[:, DRAWN] & ~previous)
        # Each claimant owns the home, meets the income test, and files alone.
        np.testing.assert_array_equal(
            np.asarray(simulation.calculate("wa_pte_eligible", year)).reshape(
                -1, len(VARIANTS)
            ),
            eligible,
        )
