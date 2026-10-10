"""Premium conservation between Schedule A and the section 162(l) deduction.

IRC 162(l)(3) excludes premiums deducted under section 162(l) from medical
expenses under section 213. Hypothesis varies earnings caps, covered premium
subsets, direct/decomposed premium inputs, spouses, dependents and separate
tax units.
The independent accounting invariant is that Schedule A's premium base plus
the self-employed health insurance deduction never exceeds premiums paid.
Non-premium medical expenses must remain available in full before the floor.

Each example uses one small vectorized simulation and a shared read-only
reference system. YAML covers the individual policy examples; these properties
check conservation across generated combinations and filing-unit boundaries.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

PERIOD = "2025"


@pytest.fixture(scope="module")
def reference_system():
    return system


@st.composite
def person_expenses(draw):
    premiums = draw(st.integers(0, 25_000))
    direct = draw(st.booleans())
    self_employed = draw(st.booleans())
    covered = draw(st.integers(0, premiums)) if self_employed else 0
    # A direct premium can also exercise the default derivation of the SE
    # premium input. Decomposed premiums need the covered subset explicitly.
    if direct and draw(st.booleans()):
        covered = None
    return {
        "premiums": premiums,
        "other": draw(st.integers(0, 10_000)),
        "earnings": draw(st.integers(-25_000, 50_000)) if self_employed else 0,
        "self_employed": self_employed,
        "direct": direct,
        "covered": covered,
    }


units = st.lists(
    st.lists(person_expenses(), min_size=1, max_size=3),
    min_size=2,
    max_size=4,
)


@st.composite
def units_with_deduction(draw):
    members = draw(units)
    deductions = [
        # The head's and spouse's deduction covers their premium pool. A
        # dependent's own SE deduction belongs on their separate return.
        draw(st.integers(0, sum(person["premiums"] for person in unit[:2])))
        for unit in members
    ]
    return members, deductions


def _simulation(members, reference_system, deductions=None):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for unit_index, unit in enumerate(members):
        names = []
        for person_index, person in enumerate(unit):
            name = f"person_{unit_index}_{person_index}"
            names.append(name)
            premium_variable = (
                "health_insurance_premiums"
                if person["direct"]
                else "health_insurance_premiums_without_medicare_part_b"
            )
            values = {
                "age": 12 if person_index == 2 else 40,
                "is_tax_unit_head": person_index == 0,
                "is_tax_unit_spouse": person_index == 1,
                "is_tax_unit_dependent": person_index == 2,
                "is_self_employed": person["self_employed"],
                "self_employment_income": person["earnings"],
                "medicare_enrolled": False,
                premium_variable: person["premiums"],
                "other_medical_expenses": person["other"],
            }
            if person["covered"] is not None:
                values["self_employed_health_insurance_premiums"] = person["covered"]
            people[name] = {
                variable: {PERIOD: value} for variable, value in values.items()
            }
        tax_unit = {"members": names}
        if deductions is not None:
            tax_unit["self_employed_health_insurance_ald"] = {
                PERIOD: deductions[unit_index]
            }
        tax_units[f"tax_unit_{unit_index}"] = tax_unit
        households[f"household_{unit_index}"] = {
            "members": names,
            "state_code": {PERIOD: "TX"},
        }
        marital_units[f"marital_unit_{unit_index}"] = {"members": names[:2]}
        for name in names[2:]:
            marital_units[f"dependent_marital_unit_{unit_index}"] = {"members": [name]}
    return Simulation(
        tax_benefit_system=reference_system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        },
    )


def _assert_conservation(members, simulation):
    paid = np.array([sum(person["premiums"] for person in unit) for unit in members])
    other = np.array([sum(person["other"] for person in unit) for unit in members])
    dependent_premiums = np.array(
        [sum(person["premiums"] for person in unit[2:]) for unit in members]
    )
    medical_base = simulation.calculate("itemized_medical_expenses", PERIOD)
    se_deduction = simulation.calculate("self_employed_health_insurance_ald", PERIOD)
    schedule_a_premium_use = medical_base - other

    # Neither the SE deduction nor a different filing unit can consume the
    # non-premium expenses. Check the bound separately from conservation.
    assert (schedule_a_premium_use >= 0).all()
    assert (schedule_a_premium_use >= dependent_premiums).all()
    assert (schedule_a_premium_use + se_deduction <= paid).all()
    # All premiums here are otherwise eligible: unused premiums remain in
    # Schedule A's base, even when earnings cap the SE deduction.
    np.testing.assert_array_equal(schedule_a_premium_use + se_deduction, paid)


EXAMPLE_UNITS = [
    [
        dict(
            premiums=6_000,
            other=500,
            earnings=1_000,
            self_employed=True,
            direct=True,
            covered=None,
        ),
        dict(
            premiums=2_000,
            other=300,
            earnings=5_000,
            self_employed=True,
            direct=False,
            covered=1_000,
        ),
        dict(
            premiums=12_000,
            other=200,
            earnings=15_000,
            self_employed=True,
            direct=True,
            covered=None,
        ),
    ],
    [
        dict(
            premiums=5_000,
            other=700,
            earnings=-2_000,
            self_employed=True,
            direct=True,
            covered=None,
        )
    ],
]


@settings(max_examples=12, deadline=None, derandomize=True)
@example(members=EXAMPLE_UNITS)
@given(members=units)
def test_premiums_are_not_duplicated_with_derived_se_deduction(
    reference_system, members
):
    _assert_conservation(members, _simulation(members, reference_system))


@settings(max_examples=12, deadline=None, derandomize=True)
@example(case=(EXAMPLE_UNITS, [8_000, 0]))
@given(case=units_with_deduction())
def test_premiums_are_not_duplicated_with_tax_unit_se_deduction(reference_system, case):
    members, deductions = case
    _assert_conservation(
        members, _simulation(members, reference_system, deductions=deductions)
    )
