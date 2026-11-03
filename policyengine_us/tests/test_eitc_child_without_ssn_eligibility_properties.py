"""Properties of EITC eligibility for a filer whose qualifying child lacks a
valid SSN.

From 2021 (ARPA section 9622 struck former IRC 32(c)(1)(F)), such a filer is
an eligible individual with a qualifying child (32(c)(1)(A)(i)); the child is
left out only of the amount (32(c)(3)(D), (m)). So from 2021:

1. The filer with the child gets the same EITC as an age-40 childless twin
   with the same earnings: the zero-child amount does not depend on age, and
   the twin always meets the childless age test.
2. The SSN-filtered child count stays zero.
3. The filer alone gets the twin's EITC if the filer meets the childless age
   test (32(c)(1)(A)(ii)(II)), and nothing otherwise: being the head never
   stands in for a qualifying child.

Before 2021 the identification-filtered count decides eligibility, and former
32(c)(1)(F) can only deny the credit, so:

4. Adding a qualifying child without an SSN never raises the EITC.

Every input that decides qualifying-child status is left to the formulas: no
person sets is_eitc_qualifying_child. Each example builds one simulation in
which every filer appears three times: alone, with a child without an SSN,
and as an age-40 childless twin.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
import numpy as np

from policyengine_us import Simulation

FILER = st.fixed_dictionaries(
    {
        "age": st.one_of(
            st.sampled_from([17, 18, 19, 23, 24, 25, 64, 65]),
            st.integers(min_value=16, max_value=80),
        ),
        "student": st.booleans(),
        "earnings": st.integers(min_value=0, max_value=30_000),
        "child_has_tin": st.booleans(),
    }
)

VARIANTS = ("alone", "with_child", "adult_alone")


def _simulate(year, filers):
    people, tax_units, households = {}, {}, {}
    for i, filer in enumerate(filers):
        for variant in VARIANTS:
            name = f"u{i}_{variant}"
            members = [f"{name}_f"]
            people[f"{name}_f"] = {
                "age": {year: 40 if variant == "adult_alone" else filer["age"]},
                "is_full_time_student": {year: filer["student"]},
                "ssn_card_type": {year: "CITIZEN"},
                "employment_income": {year: filer["earnings"]},
            }
            if variant == "with_child":
                members.append(f"{name}_c")
                people[f"{name}_c"] = {
                    "age": {year: 2},
                    "is_tax_unit_dependent": {year: True},
                    "ssn_card_type": {year: "NONE"},
                    "has_tin": {year: filer["child_has_tin"]},
                }
            tax_units[name] = {
                "members": members,
                "filing_status": {year: "SINGLE"},
                "would_file_taxes_voluntarily": {year: True},
                "takes_up_eitc": {year: True},
            }
            households[name] = {"members": members, "state_code": {year: "TX"}}
    sim = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )
    eitc = sim.calculate("eitc", year)
    count = sim.calculate("eitc_child_count", year)
    n = len(VARIANTS)
    age = sim.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age
    return eitc[0::n], eitc[1::n], eitc[2::n], count[1::n], age(f"{year}-01-01")


def _meets_childless_age_test(filers, age):
    filer_age = np.array([filer["age"] for filer in filers])
    student = np.array([filer["student"] for filer in filers])
    min_age = np.where(student, age.min_student, age.min)
    return (filer_age >= min_age) & (filer_age <= age.max)


SETTINGS = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@SETTINGS
@given(
    year=st.sampled_from([2021, 2022, 2023, 2024, 2025]),
    filers=st.lists(FILER, min_size=1, max_size=10),
)
def test_child_without_ssn_gives_zero_child_amount_from_2021(year, filers):
    alone, with_child, adult_alone, count, age = _simulate(year, filers)
    assert (count == 0).all()
    assert (abs(with_child - adult_alone) < 0.01).all()
    expected_alone = np.where(_meets_childless_age_test(filers, age), adult_alone, 0)
    assert (abs(alone - expected_alone) < 0.01).all()


@SETTINGS
@given(
    year=st.sampled_from([2018, 2019, 2020]),
    filers=st.lists(FILER, min_size=1, max_size=10),
)
def test_child_without_ssn_never_raises_eitc_before_2021(year, filers):
    # Before 2021 a qualifying child without an SSN never helps: the
    # identification-filtered count decides eligibility, and former
    # 32(c)(1)(F) can only deny the credit.
    alone, with_child, _, _, _ = _simulate(year, filers)
    assert (with_child <= alone + 0.01).all()
