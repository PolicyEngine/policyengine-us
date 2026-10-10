"""Invariants for pre-tax payroll premiums and Schedule A medical expenses.

IRC 213(a) allows "the expenses paid during the taxable year, not compensated
for by insurance or otherwise, for medical care", above 7.5% of adjusted gross
income. A premium paid by salary reduction under a section 125 cafeteria plan
is paid by the employer, not the employee, and is excluded from wages under
IRC 106(a) (Rev. Rul. 2002-3), so it is not an expense the taxpayer paid.

pre_tax_health_insurance_premiums holds those premiums. The other premium
inputs hold premiums not paid that way, and the two are disjoint: a premium is
reported in one or the other, never both.

Hypothesis draws batches of tax units (single or joint, with up to two
dependents), each person with wages, pre-tax premiums, after-tax premiums and
other medical expenses. The after-tax premiums are supplied either directly or
as non-Medicare premiums. Each batch runs as one vectorized simulation, again
with every pre-tax premium removed, and again with every pre-tax premium paid
after tax instead. For every batch:

1. Exclusion: Schedule A medical expenses equal the tax unit's after-tax
   premiums plus other medical expenses, whatever the pre-tax premiums are.
2. One tax benefit per dollar: each person's wage exclusion is their pre-tax
   premiums, up to their wages, and their Schedule A premiums are their
   after-tax premiums. The two never cover the same dollar, and together they
   never exceed the premiums paid.
3. Differential: the deduction equals an independent numpy calculation, with
   the 7.5% floor taken from the statute rather than the parameters.
4. Bounds: 0 <= deduction <= Schedule A medical expenses.
5. Payment method: paying the pre-tax premiums after tax instead raises
   Schedule A medical expenses by exactly those premiums and wages by exactly
   the wage exclusion, and never lowers the deduction. Removing the pre-tax
   premiums leaves Schedule A medical expenses unchanged and never raises the
   deduction.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.1  # dollars; incomes are float32

# IRC 213(a): "to the extent that such expenses exceed 7.5 percent of
# adjusted gross income". The rate has applied since 2017.
STATUTORY_FLOOR = 0.075
YEARS = [2024, 2026]

amounts = st.one_of(st.just(0.0), st.integers(1, 15_000).map(float))
wages = st.one_of(st.just(0.0), st.integers(1, 200_000).map(float))


@st.composite
def people(draw):
    return {
        "wages": draw(wages),
        "pre_tax": draw(amounts),
        "after_tax": draw(amounts),
        "other": draw(st.one_of(st.just(0.0), st.integers(1, 40_000).map(float))),
        # Which input carries the after-tax premiums.
        "direct": draw(st.booleans()),
    }


@st.composite
def tax_units(draw):
    return {
        "head": draw(people()),
        "spouse": draw(st.none() | people()),
        "dependents": draw(st.lists(people(), max_size=2)),
    }


def _person(wages=0.0, pre_tax=0.0, after_tax=0.0, other=0.0, direct=False):
    return {
        "wages": wages,
        "pre_tax": pre_tax,
        "after_tax": after_tax,
        "other": other,
        "direct": direct,
    }


def _situation(units, year, treatment):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}

    def add(name, values, role):
        pre_tax = values["pre_tax"] if treatment == "drawn" else 0
        after_tax = values["after_tax"]
        if treatment == "paid_after_tax":
            after_tax += values["pre_tax"]
        people[name] = {
            "age": {"head": 45, "spouse": 43, "dependent": 17}[role],
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "employment_income": values["wages"],
            "pre_tax_health_insurance_premiums": pre_tax,
            "health_insurance_premiums": after_tax * values["direct"],
            "health_insurance_premiums_without_medicare_part_b": after_tax
            * (not values["direct"]),
            "other_medical_expenses": values["other"],
            # No modeled Medicare Part B premium, so the premiums are only
            # the drawn ones.
            "medicare_enrolled": False,
        }

    for i, unit in enumerate(units):
        head = f"head_{i}"
        add(head, unit["head"], "head")
        members, couple = [head], [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            add(spouse, unit["spouse"], "spouse")
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, dependent in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            add(name, dependent, "dependent")
            members.append(name)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [name]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


PERSON = [
    "employment_income",
    "irs_employment_income",
    "medical_expense_health_insurance_premiums",
]
TAX_UNIT = [
    "adjusted_gross_income",
    "itemized_medical_expenses",
    "medical_expense_deduction",
]


def _run(units, year, treatment):
    sim = Simulation(situation=_situation(units, year, treatment))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON + TAX_UNIT
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _members(units):
    return [
        person
        for unit in units
        for person in [unit["head"], unit["spouse"], *unit["dependents"]]
        if person is not None
    ]


def _check(units, year):
    drawn = _run(units, year, "drawn")
    unit = drawn["unit"]
    members = _members(units)
    pre_tax = np.array([person["pre_tax"] for person in members])
    after_tax = np.array([person["after_tax"] for person in members])
    other = np.array([person["other"] for person in members])
    earned = np.array([person["wages"] for person in members])
    np.testing.assert_array_equal(drawn["employment_income"], earned)

    def unit_sum(values):
        return np.bincount(unit, weights=values, minlength=len(units))

    expenses = drawn["itemized_medical_expenses"]
    deduction = drawn["medical_expense_deduction"]

    # 1. Exclusion, against the drawn amounts.
    np.testing.assert_allclose(expenses, unit_sum(after_tax + other), atol=TOLERANCE)

    # 2. One tax benefit per dollar.
    wage_exclusion = earned - drawn["irs_employment_income"]
    schedule_a_premiums = drawn["medical_expense_health_insurance_premiums"]
    np.testing.assert_allclose(
        wage_exclusion, np.minimum(pre_tax, earned), atol=TOLERANCE
    )
    np.testing.assert_allclose(schedule_a_premiums, after_tax, atol=TOLERANCE)
    assert (
        wage_exclusion + schedule_a_premiums <= pre_tax + after_tax + TOLERANCE
    ).all()

    # 3. Differential against an independent calculation.
    agi = drawn["adjusted_gross_income"]
    expected = np.maximum(
        unit_sum(after_tax + other) - STATUTORY_FLOOR * np.maximum(agi, 0), 0
    )
    np.testing.assert_allclose(deduction, expected, atol=TOLERANCE)

    # 4. Bounds.
    assert (deduction >= 0).all()
    assert (deduction <= expenses + TOLERANCE).all()

    # 5. Payment method.
    removed = _run(units, year, "removed")
    np.testing.assert_allclose(
        removed["itemized_medical_expenses"], expenses, atol=TOLERANCE
    )
    np.testing.assert_allclose(removed["irs_employment_income"], earned, atol=TOLERANCE)
    assert (removed["medical_expense_deduction"] <= deduction + TOLERANCE).all()

    paid_after_tax = _run(units, year, "paid_after_tax")
    np.testing.assert_allclose(
        paid_after_tax["itemized_medical_expenses"] - expenses,
        unit_sum(pre_tax),
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        paid_after_tax["irs_employment_income"], earned, atol=TOLERANCE
    )
    assert (paid_after_tax["medical_expense_deduction"] >= deduction - TOLERANCE).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)

EDGE_CASES = [
    # Nothing paid.
    {"head": _person(wages=50_000), "spouse": None, "dependents": []},
    # Pre-tax premiums only.
    {
        "head": _person(wages=60_000, pre_tax=2_000, other=9_000),
        "spouse": None,
        "dependents": [],
    },
    # Pre-tax premiums above wages: the wage exclusion stops at wages.
    {
        "head": _person(wages=1_000, pre_tax=2_500, after_tax=400, direct=True),
        "spouse": None,
        "dependents": [],
    },
    # Each spouse pays a different way, and a working dependent pays both.
    {
        "head": _person(wages=50_000, pre_tax=2_400, other=6_000),
        "spouse": _person(wages=30_000, after_tax=1_800, other=1_000, direct=True),
        "dependents": [_person(wages=8_000, pre_tax=600, after_tax=300, other=250)],
    },
]


@settings(**SETTINGS)
@example(year=2025, units=EDGE_CASES)
@given(
    year=st.sampled_from(YEARS),
    units=st.lists(tax_units(), min_size=5, max_size=30),
)
def test_schedule_a_pre_tax_premium_invariants(year, units):
    _check(units, year)
