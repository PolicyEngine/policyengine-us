"""Invariants for the West Virginia senior citizen or disability deduction.

Each eligible spouse may subtract up to $8,000 of federal AGI, less their own
Schedule M modifications on lines 29 through 34 (box (d) of line 47). Jointly
owned income is divided by ownership, so each spouse counts only their own
interest on U.S. obligations (2025 IT-140 instructions, pages 27-28; W. Va.
Code 11-21-12(c)(9)).

The properties must hold for every person, so the tests draw a seeded random
population of West Virginia tax units (single, joint, joint with a dependent)
with wages, pensions, military retirement and U.S. obligation interest, and run
it twice as vectorized simulations: as drawn, and with all U.S. obligation
interest set to zero.

1. A person's modifications rise by exactly their own U.S. obligation
   interest, so a spouse's interest never reduces the other spouse's deduction.
2. Each person's deduction is between zero and $8,000, and zero for anyone
   who is not eligible.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
N_RANDOM = 200
SEED = 20261006
CAP = 8_000
TOLERANCE = 0.02  # dollars; float32 sums


def _situation(zero_interest=False):
    rng = np.random.default_rng(SEED)
    people, tax_units, households = {}, {}, {}
    for i in range(N_RANDOM):
        kind = rng.choice(["single", "joint", "joint", "joint_dependent"])
        roles = ["head"] if kind == "single" else ["head", "spouse"]
        members = []
        for role in roles:
            name = f"{role}_{i}"
            members.append(name)
            interest = float(round(rng.choice([0.0, rng.uniform(0, 6_000)])))
            people[name] = {
                "age": {YEAR: int(rng.integers(55, 85))},
                "employment_income": {
                    YEAR: float(round(rng.choice([0.0, rng.uniform(0, 30_000)])))
                },
                "taxable_pension_income": {
                    YEAR: float(round(rng.choice([0.0, rng.uniform(0, 20_000)])))
                },
                "military_retirement_pay": {
                    YEAR: float(round(rng.choice([0.0, 0.0, rng.uniform(0, 9_000)])))
                },
                "us_govt_interest_person": {YEAR: 0.0 if zero_interest else interest},
                f"is_tax_unit_{role}": {YEAR: True},
            }
        if kind == "joint_dependent":
            name = f"child_{i}"
            members.append(name)
            people[name] = {"age": {YEAR: 12}, "is_tax_unit_dependent": {YEAR: True}}
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {"members": members, "state_code": {YEAR: "WV"}}
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def run():
    out = {}
    for name, zero_interest in {"with": False, "without": True}.items():
        sim = Simulation(situation=_situation(zero_interest=zero_interest))
        for variable in [
            "wv_senior_citizen_disability_deduction_total_modifications",
            "wv_senior_citizen_disability_deduction_person",
        ]:
            out[(name, variable)] = np.asarray(
                sim.calculate(variable, YEAR), dtype=float
            )
        if name == "with":
            out["interest"] = np.asarray(
                sim.calculate("us_govt_interest_person", YEAR), dtype=float
            )
            out["eligible"] = np.asarray(
                sim.calculate(
                    "wv_senior_citizen_disability_deduction_eligible_person", YEAR
                )
            )
            out["is_tax_unit_spouse"] = np.asarray(
                sim.calculate("is_tax_unit_spouse", YEAR)
            )
    return out


def test_population_has_eligible_spouses_with_interest(run):
    spouse_interest = run["is_tax_unit_spouse"] & (run["interest"] > 0)
    assert (spouse_interest & run["eligible"]).sum() > 20


def test_modifications_rise_by_own_interest_only(run):
    variable = "wv_senior_citizen_disability_deduction_total_modifications"
    np.testing.assert_allclose(
        run[("with", variable)] - run[("without", variable)],
        run["interest"],
        atol=TOLERANCE,
    )


def test_interest_never_raises_a_deduction(run):
    variable = "wv_senior_citizen_disability_deduction_person"
    assert np.all(run[("with", variable)] <= run[("without", variable)] + TOLERANCE)


def test_deduction_within_bounds(run):
    deduction = run[("with", "wv_senior_citizen_disability_deduction_person")]
    assert np.all((deduction >= 0) & (deduction <= CAP))
    assert np.all(deduction[~run["eligible"]] == 0)
