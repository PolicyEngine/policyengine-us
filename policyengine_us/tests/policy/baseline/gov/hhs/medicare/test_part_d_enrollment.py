"""The Part D income-related premium applies only to Part D enrollees.

42 U.S.C. 1395w-113(a)(7) raises the Part D beneficiary premium, which only
Part D enrollees pay. Invariants checked for every drawn set of people:
- the surcharge is never negative and is zero for anyone not in Part D;
- for Part D enrollees it equals the surcharge when every Medicare enrollee
  takes up Part D, so the enrollment gate removes charges and changes none;
- Part D enrollment implies Medicare enrollment, which implies eligibility;
- Part D take-up leaves the Part B premium unchanged.

Each example builds two small simulations on the shared model system; no
extra tax-benefit system stays resident.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
    "SEPARATE",
]
# Years with brackets of their own.
YEARS = [2024, 2025, 2026]

PERSON = st.fixed_dictionaries(
    {
        "age": st.integers(min_value=55, max_value=95),
        "takes_up_medicare": st.booleans(),
        "takes_up_part_d": st.booleans(),
        # MAGI is stored as float32; draw values it can hold.
        "magi": st.floats(min_value=0, max_value=1_500_000, width=32),
        "filing_status": st.sampled_from(FILING_STATUSES),
    }
)


def simulate(people, year, everyone_takes_up_part_d):
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, person in enumerate(people):
        name = f"person_{i}"
        situation["people"][name] = {
            "age": {year: person["age"]},
            "takes_up_medicare_if_eligible": {year: person["takes_up_medicare"]},
            "takes_up_medicare_part_d_if_eligible": {
                year: everyone_takes_up_part_d or person["takes_up_part_d"]
            },
        }
        situation["tax_units"][f"tax_unit_{i}"] = {
            "members": [name],
            "filing_status": {year: person["filing_status"]},
            "medicare_irmaa_magi_two_years_prior": {year: person["magi"]},
        }
        situation["households"][f"household_{i}"] = {"members": [name]}
    return Simulation(situation=situation)


@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    people=st.lists(PERSON, min_size=1, max_size=8),
    year=st.sampled_from(YEARS),
)
def test_part_d_surcharge_applies_only_to_part_d_enrollees(people, year):
    sim = simulate(people, year, everyone_takes_up_part_d=False)
    everyone = simulate(people, year, everyone_takes_up_part_d=True)

    surcharge = sim.calculate("income_adjusted_part_d_premium_surcharge", year)
    surcharge_if_all_enroll = everyone.calculate(
        "income_adjusted_part_d_premium_surcharge", year
    )
    part_d = sim.calculate("medicare_part_d_enrolled", year)
    enrolled = sim.calculate("medicare_enrolled", year)
    eligible = sim.calculate("is_medicare_eligible", year)
    takes_up_part_d = np.array([person["takes_up_part_d"] for person in people])

    assert (surcharge >= 0).all()
    assert (surcharge[~part_d] == 0).all()
    np.testing.assert_array_equal(surcharge[part_d], surcharge_if_all_enroll[part_d])
    np.testing.assert_array_equal(part_d, enrolled & takes_up_part_d)
    assert (~part_d | enrolled).all()
    assert (~enrolled | eligible).all()
    np.testing.assert_array_equal(
        sim.calculate("gross_medicare_part_b_premium", year),
        everyone.calculate("gross_medicare_part_b_premium", year),
    )
