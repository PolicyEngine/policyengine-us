"""Invariants for the D.C. self-employment loss addition.

The addition adds back the filers' self-employment losses deducted in federal
AGI above D.C.'s $12,000 threshold (Schedule I, Calculation A, line 6). A
tax-unit dependent's losses belong on the dependent's own return and are not in
`loss_ald`, so they must not enter the addition or its split between spouses.

The properties must hold for every tax unit, so the tests draw a seeded random
population of D.C. tax units (single, head of household, joint, joint with
dependents) whose members have wages and self-employment income of either sign,
and run it twice as vectorized simulations: as drawn, and with the dependents'
self-employment income set to zero.

1. Dependents' self-employment income never changes anyone's addition.
2. Dependents get no addition, and no addition is negative.
3. A joint return splits the addition between the spouses in proportion to
   their own losses.
4. The tax unit's addition never exceeds the filers' losses less $12,000.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
N_RANDOM = 200
SEED = 20261006
THRESHOLD = 12_000
TOLERANCE = 0.02  # dollars; float32 sums


def _self_employment(rng, low, high):
    return float(round(rng.choice([0.0, rng.uniform(low, 0), rng.uniform(0, high)])))


def _situation(zero_dependents=False):
    rng = np.random.default_rng(SEED)
    people, tax_units, households = {}, {}, {}
    for i in range(N_RANDOM):
        kind = rng.choice(
            ["single", "hoh", "joint", "joint_dependents"], p=[0.15, 0.2, 0.2, 0.45]
        )
        roles = ["head", "spouse"] if kind.startswith("joint") else ["head"]
        members = []
        for role in roles:
            name = f"{role}_{i}"
            members.append(name)
            people[name] = {
                "age": {YEAR: 45},
                "employment_income": {YEAR: float(round(rng.uniform(0, 150_000)))},
                "self_employment_income": {
                    YEAR: _self_employment(rng, -60_000, 40_000)
                },
                f"is_tax_unit_{role}": {YEAR: True},
            }
        if kind in ("hoh", "joint_dependents"):
            for j in range(int(rng.integers(1, 3))):
                name = f"child_{i}_{j}"
                members.append(name)
                amount = _self_employment(rng, -40_000, 20_000)
                people[name] = {
                    "age": {YEAR: 16 + j},
                    "is_tax_unit_dependent": {YEAR: True},
                    "self_employment_income": {
                        YEAR: 0.0 if zero_dependents else amount
                    },
                }
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {"members": members, "state_code": {YEAR: "DC"}}
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def run():
    out = {}
    for name, zero_dependents in {"with": False, "without": True}.items():
        sim = Simulation(situation=_situation(zero_dependents=zero_dependents))
        out[name] = np.asarray(
            sim.calculate("dc_self_employment_loss_addition", YEAR), dtype=float
        )
        if name == "with":
            for variable in [
                "total_self_employment_income",
                "is_tax_unit_dependent",
                "is_tax_unit_spouse",
            ]:
                out[variable] = np.asarray(sim.calculate(variable, YEAR))
            out["joint"] = (
                sim.calculate("filing_status", YEAR).decode_to_str() == "JOINT"
            )
            out["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["person_tax_unit"], weights=values, minlength=len(run["joint"])
    )


def test_population_has_dependent_losses_and_additions(run):
    dependent = run["is_tax_unit_dependent"]
    dependent_loss = _unit_sum(
        run, dependent * (run["total_self_employment_income"] < 0)
    )
    added = _unit_sum(run, run["with"]) > 0
    assert ((dependent_loss > 0) & added & run["joint"]).sum() > 5


def test_dependents_income_never_changes_the_addition(run):
    np.testing.assert_allclose(run["with"], run["without"], atol=TOLERANCE)


def test_dependents_get_nothing_and_nothing_is_negative(run):
    assert np.all(run["with"][run["is_tax_unit_dependent"]] == 0)
    assert np.all(run["with"] >= 0)


def test_joint_split_follows_each_spouses_loss(run):
    loss = np.maximum(0, -run["total_self_employment_income"])
    filer = ~run["is_tax_unit_dependent"]
    unit_loss = _unit_sum(run, filer * loss)
    unit_addition = _unit_sum(run, run["with"])
    joint_filer = filer & run["joint"][run["person_tax_unit"]]
    expected = np.zeros_like(loss)
    has_loss = unit_loss[run["person_tax_unit"]] > 0
    share = np.divide(
        loss, unit_loss[run["person_tax_unit"]], out=expected.copy(), where=has_loss
    )
    np.testing.assert_allclose(
        run["with"][joint_filer],
        (share * unit_addition[run["person_tax_unit"]])[joint_filer],
        atol=TOLERANCE,
    )


def test_addition_never_exceeds_filers_losses_over_threshold(run):
    loss = np.maximum(0, -run["total_self_employment_income"])
    filer_loss = _unit_sum(run, ~run["is_tax_unit_dependent"] * loss)
    assert np.all(
        _unit_sum(run, run["with"]) <= np.maximum(0, filer_loss - THRESHOLD) + TOLERANCE
    )
