"""Invariants for the educator expense deduction, 26 USC 62(a)(2)(D) and (d).

Each eligible educator deducts their own qualified expenses up to the cap. On
a joint return the head's and the spouse's capped amounts add up; neither
spouse can use the other's unused room. A tax unit dependent's expenses are
on the dependent's own return, not the filer's.

Hypothesis draws batches of tax units (single, joint with zero, one or two
educators, and head of household or joint with dependents who may report
educator expenses), and a seeded population of 200 units adds breadth. Each
batch runs as one vectorized simulation, and again with every member's
expenses raised by a drawn non-negative amount. For every tax unit:

1. Bound: 0 <= educator_expense_ald <= the cap times the number of head and
   spouse with expenses, and never more than their expenses.
2. Differential: educator_expense_ald equals an independent numpy sum over
   the head and spouse of min(expenses, cap), with the cap taken from the
   Rev. Procs. rather than from the model's parameters. Each person's own
   amount, dependents included, is min(expenses, cap).
3. Monotone: raising expenses never lowers educator_expense_ald and never
   raises AGI. Raising only dependents' expenses changes neither.
4. Accounting: with wages as the only income and no other deductions, AGI is
   wages less educator_expense_ald.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Per-educator caps from the Rev. Procs. for each taxable year: 2020-45
# sec. 3.14 (2021), 2021-45 sec. 3.13 (2022), 2024-40 sec. 2.13 (2025) and
# 2025-32 sec. 4.12 (2026).
PUBLISHED_CAP = {2021: 250, 2022: 300, 2025: 300, 2026: 350}
YEARS = sorted(PUBLISHED_CAP)

# Mostly amounts near the caps, plus zeros and large amounts.
expenses = st.one_of(
    st.just(0.0),
    st.integers(1, 600).map(float),
    st.integers(600, 5_000).map(float),
)
increases = st.one_of(st.just(0.0), st.integers(1, 500).map(float))
wages = st.integers(0, 150_000).map(float)


@st.composite
def people(draw):
    return {
        "employment_income": draw(wages),
        "educator_expense": draw(expenses),
        "increase": draw(increases),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "hoh", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people()) for _ in range(n_dependents)],
    }


SEED = 20261005


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def person():
        expense = rng.choice([0, 1, 2])
        return {
            "employment_income": float(rng.integers(0, 150_001)),
            "educator_expense": float(
                [0, rng.integers(1, 601), rng.integers(600, 5_001)][expense]
            ),
            "increase": float(rng.integers(0, 501)) if rng.random() < 0.7 else 0.0,
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "hoh", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person() for _ in range(n_dependents)],
            }
        )
    return units


def _situation(units, year, *, raise_filers, raise_dependents):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}

    def add(name, values, role, raised):
        expense = values["educator_expense"] + raised * values["increase"]
        people[name] = {
            "age": {"head": 45, "spouse": 43, "dependent": 20}[role],
            "is_full_time_student": role == "dependent",
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "employment_income": values["employment_income"],
            "educator_expense": expense,
        }

    for i, unit in enumerate(units):
        head = f"head_{i}"
        add(head, unit["head"], "head", raise_filers)
        members, couple = [head], [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            add(spouse, unit["spouse"], "spouse", raise_filers)
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, dependent in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            add(name, dependent, "dependent", raise_dependents)
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


def _run(units, year, *, raise_filers=False, raise_dependents=False):
    sim = Simulation(
        situation=_situation(
            units,
            year,
            raise_filers=raise_filers,
            raise_dependents=raise_dependents,
        )
    )
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            "educator_expense",
            "educator_expense_ald_person",
            "employment_income",
            "educator_expense_ald",
            "above_the_line_deductions",
            "adjusted_gross_income",
        ]
    }
    out["filer"] = np.asarray(sim.calculate("is_tax_unit_head_or_spouse", year))
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"], weights=values, minlength=len(run["educator_expense_ald"])
    )


def _check(units, year):
    cap = PUBLISHED_CAP[year]
    base = _run(units, year)
    filer = base["filer"]
    expense = base["educator_expense"]

    # 1. Bounds.
    deduction = base["educator_expense_ald"]
    educators = _unit_sum(base, (filer & (expense > 0)).astype(float))
    assert (deduction >= 0).all()
    assert (deduction <= cap * educators + TOLERANCE).all()
    assert (deduction <= _unit_sum(base, filer * expense) + TOLERANCE).all()

    # 2. Differential against numpy.
    own = np.minimum(expense, cap)
    np.testing.assert_allclose(base["educator_expense_ald_person"], own, atol=TOLERANCE)
    np.testing.assert_allclose(deduction, _unit_sum(base, filer * own), atol=TOLERANCE)
    np.testing.assert_allclose(
        base["above_the_line_deductions"], deduction, atol=TOLERANCE
    )

    # 3. Monotone in expenses.
    raised = _run(units, year, raise_filers=True, raise_dependents=True)
    assert (raised["educator_expense_ald"] >= deduction - TOLERANCE).all()
    assert (
        raised["adjusted_gross_income"] <= base["adjusted_gross_income"] + TOLERANCE
    ).all()
    dependents_only = _run(units, year, raise_dependents=True)
    for name in ["educator_expense_ald", "adjusted_gross_income"]:
        np.testing.assert_allclose(
            dependents_only[name], base[name], atol=TOLERANCE, err_msg=name
        )

    # 4. Accounting identity.
    np.testing.assert_allclose(
        base["adjusted_gross_income"],
        _unit_sum(base, filer * base["employment_income"]) - deduction,
        atol=TOLERANCE,
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_educator_expense_cap_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
