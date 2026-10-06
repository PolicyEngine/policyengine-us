"""Invariants for Mississippi's health savings account adjustment.

Mississippi excludes health savings account contributions from the account
holder's gross income (Miss. Code Ann. § 71-9-11(3)), and Form 80-105 reports
each spouse's adjustments in their own column. The model's deduction,
`health_savings_account_ald`, is a tax-unit amount, so it must reach the
members' Mississippi adjustments once, not once per member.

Hypothesis draws batches of Mississippi tax units (single, married filing
separately, head of household with dependents, joint with and without
dependents), with the tax unit's deduction either equal to the head's and
spouse's own `health_savings_account_ald_person` amounts, different from
them, or given without them; a seeded population adds breadth. Each batch runs
as one vectorized simulation, twice: as drawn and with the tax unit's
deduction set to zero. For every tax unit:

1. Conservation: the members' `ms_health_savings_account_adjustment` sum to
   the tax unit's `health_savings_account_ald`, and the deduction appears in
   the members' `ms_agi_adjustments` exactly once.
2. Bounds: no share is negative or above the tax unit's deduction, and a
   dependent's is zero.
3. Differential: each share equals an independent numpy attribution (own
   amounts scaled to the tax unit's deduction; the head takes it without
   them), which is each filer's own amount when those sum to the deduction.
4. The deduction lowers the members' total Mississippi AGI by at least zero
   and at most the deduction itself.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
HSA = "ms_health_savings_account_adjustment"

amount = st.integers(0, 60_000).map(float)
hsa = st.one_of(st.just(0.0), st.integers(1, 8_550).map(float))


@st.composite
def person_amounts(draw, *, dependent):
    return {
        "employment_income": draw(st.one_of(st.just(0.0), amount)),
        "self_employment_income": draw(
            st.one_of(st.just(0.0), st.integers(-5_000, 40_000).map(float))
        ),
        "traditional_ira_contributions": draw(
            st.one_of(st.just(0.0), st.integers(1, 7_000).map(float))
        ),
        "health_savings_account_ald_person": 0.0 if dependent else draw(hsa),
    }


@st.composite
def tax_units(draw):
    kind = draw(
        st.sampled_from(["single", "separate", "hoh", "joint", "joint_dependents"])
    )
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    head = draw(person_amounts(dependent=False))
    spouse = draw(person_amounts(dependent=False)) if kind.startswith("joint") else None
    own = head["health_savings_account_ald_person"] + (
        spouse["health_savings_account_ald_person"] if spouse else 0.0
    )
    # The tax unit's deduction: the filers' own amounts, a different amount,
    # or zero.
    deduction = draw(st.sampled_from(["own", "other", "zero"]))
    return {
        "kind": kind,
        "head": head,
        "spouse": spouse,
        "dependents": [
            {"age": draw(st.integers(5, 23)), **draw(person_amounts(dependent=True))}
            for _ in range(n_dependents)
        ],
        "health_savings_account_ald": {
            "own": own,
            "other": draw(hsa),
            "zero": 0.0,
        }[deduction],
    }


SEED = 20261006


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(high, p=0.5, low=1):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def amounts(dependent):
        return {
            "employment_income": some(60_000, 0.7),
            "self_employment_income": some(40_000, 0.3, low=-5_000),
            "traditional_ira_contributions": some(7_000, 0.3),
            "health_savings_account_ald_person": 0.0 if dependent else some(8_550),
        }

    units = []
    for _ in range(n):
        kind = str(
            rng.choice(["single", "separate", "hoh", "joint", "joint_dependents"])
        )
        head = amounts(False)
        spouse = amounts(False) if kind.startswith("joint") else None
        own = head["health_savings_account_ald_person"] + (
            spouse["health_savings_account_ald_person"] if spouse else 0.0
        )
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "kind": kind,
                "head": head,
                "spouse": spouse,
                "dependents": [
                    {"age": int(rng.integers(5, 24)), **amounts(True)}
                    for _ in range(n_dependents)
                ],
                "health_savings_account_ald": float(
                    rng.choice([own, some(8_550, 1.0), 0.0])
                ),
            }
        )
    return units


def _situation(units, year, *, zero_deduction):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {"age": 45, **u["head"]}
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": 43, **u["spouse"]}
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            people[child] = {
                "age": d["age"],
                "is_full_time_student": d["age"] >= 19,
                **{k: v for k, v in d.items() if k != "age"},
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        tax_unit = {
            "members": members,
            "health_savings_account_ald": (
                0.0 if zero_deduction else u["health_savings_account_ald"]
            ),
        }
        if u["kind"] == "separate":
            tax_unit["filing_status"] = "SEPARATE"
        groups["tax_units"][f"tax_unit_{i}"] = tax_unit
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": "MS",
        }

    def by_year(values):
        return {k: (v if k == "members" else {year: v}) for k, v in values.items()}

    return {
        "people": {name: by_year(values) for name, values in people.items()},
        **{
            plural: {name: by_year(values) for name, values in entities.items()}
            for plural, entities in groups.items()
        },
    }


def _run(units, year, *, zero_deduction):
    sim = Simulation(situation=_situation(units, year, zero_deduction=zero_deduction))
    adjustments = sim.tax_benefit_system.parameters(
        year
    ).gov.states.ms.tax.income.adjustments.adjustments
    others = [name for name in adjustments if "health_savings_account" not in name]
    person = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            HSA,
            "ms_agi_adjustments",
            "ms_agi",
            "health_savings_account_ald_person",
        ]
    }
    person["other_adjustments"] = sum(
        np.asarray(sim.calculate(name, year), dtype=float) for name in others
    )
    person["is_head"] = np.asarray(sim.calculate("is_tax_unit_head", year), dtype=bool)
    person["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    person["unit"] = sim.populations["tax_unit"].members_entity_id
    deduction = np.asarray(
        sim.calculate("health_savings_account_ald", year), dtype=float
    )
    return person, deduction


def _unit_sum(person, values, n):
    return np.bincount(person["unit"], weights=values, minlength=n)


def _reference_shares(person, deduction):
    """Attribution of the tax unit's deduction, computed independently."""
    unit = person["unit"]
    filer = ~person["is_dependent"]
    own = person["health_savings_account_ald_person"] * filer
    filers_own = np.bincount(unit, weights=own, minlength=len(deduction))
    scaled = np.divide(
        own * deduction[unit],
        filers_own[unit],
        out=np.zeros_like(own),
        where=filers_own[unit] > 0,
    )
    head_takes_it = person["is_head"] * (filers_own[unit] == 0) * deduction[unit]
    return np.where(filer, scaled + head_takes_it, 0.0)


def _check(units, year):
    person, deduction = _run(units, year, zero_deduction=False)
    without, _ = _run(units, year, zero_deduction=True)
    n = len(deduction)
    shares = person[HSA]

    # 1. Conservation: the deduction is attributed, and subtracted, once.
    np.testing.assert_allclose(_unit_sum(person, shares, n), deduction, atol=TOLERANCE)
    np.testing.assert_allclose(
        _unit_sum(
            person, person["ms_agi_adjustments"] - person["other_adjustments"], n
        ),
        deduction,
        atol=TOLERANCE,
    )

    # 2. Bounds.
    unit = person["unit"]
    assert (shares >= -TOLERANCE).all()
    assert (shares <= deduction[unit] + TOLERANCE).all()
    assert (shares[person["is_dependent"]] == 0).all()

    # 3. Differential against an independent attribution, which honours each
    # filer's own amount whenever those sum to the deduction.
    np.testing.assert_allclose(
        shares, _reference_shares(person, deduction), atol=TOLERANCE
    )
    filer = ~person["is_dependent"]
    filers_own = _unit_sum(
        person, person["health_savings_account_ald_person"] * filer, n
    )
    matches = (np.abs(filers_own - deduction) < TOLERANCE)[unit] & filer
    np.testing.assert_allclose(
        shares[matches],
        person["health_savings_account_ald_person"][matches],
        atol=TOLERANCE,
    )

    # 4. The deduction lowers total Mississippi AGI by no more than itself.
    reduction = _unit_sum(without, without["ms_agi"], n) - _unit_sum(
        person, person["ms_agi"], n
    )
    assert (reduction >= -TOLERANCE).all()
    assert (reduction <= deduction + TOLERANCE).all()


SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_ms_health_savings_account_adjustment_is_attributed_once(units):
    _check(units, 2025)


@pytest.mark.parametrize("year", [2022, 2025, 2026])
def test_seeded_population(year):
    _check(_seeded_units(), year)
