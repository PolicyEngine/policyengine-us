"""Invariants for the Kentucky family size tax credit on each filing path.

KRS 141.066(4) computes the credit from joint modified gross income on a joint
return. When spouses file separately on a combined return, it uses their
combined modified gross income, with a separately computed amount below zero
treated as zero. The combined-separate election compares the two paths, so each
path needs its own rate.

The properties must hold for every tax unit, so the tests draw a seeded random
population of Kentucky tax units (single, joint, joint with dependents) whose
adults have wages, pensions and self-employment income of either sign, and run
it as one vectorized simulation:

1. A member's negative federal or Kentucky AGI never offsets another member's
   income on the combined-separate path: its modified gross income is at least
   every member's federal and Kentucky AGI, and at least the joint amount. With
   no negative member, the two paths agree.
2. The combined-separate credit rate never exceeds the joint rate (the rate
   falls as modified gross income rises).
3. The elected modified gross income and rate are the elected path's.
4. Tax before refundable credits from the post-election credit chain equals the
   elected path's value from the election helper, and married couples pay the
   lower of the two paths.
"""

import numpy as np
import pytest

from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.states.ky.graduated_income_tax.ky_graduated_income_tax_reform import (
    ky_graduated_income_tax,
)

YEAR = 2025
N_RANDOM = 200
SEED = 20261006
TOLERANCE = 0.02  # dollars; float32 sums


def _situation():
    rng = np.random.default_rng(SEED)
    people, tax_units, households = {}, {}, {}
    for i in range(N_RANDOM):
        kind = rng.choice(["single", "joint", "joint_dependents"])
        roles = ["head"] if kind == "single" else ["head", "spouse"]
        members = []
        for role in roles:
            name = f"{role}_{i}"
            members.append(name)
            self_employment = rng.choice(
                [0.0, rng.uniform(-40_000, 0), rng.uniform(0, 30_000)]
            )
            people[name] = {
                "age": {YEAR: int(rng.integers(25, 80))},
                "employment_income": {
                    YEAR: float(round(rng.choice([0.0, rng.uniform(0, 60_000)])))
                },
                "self_employment_income": {YEAR: float(round(self_employment))},
                "taxable_pension_income": {
                    YEAR: float(round(rng.choice([0.0, 0.0, rng.uniform(0, 40_000)])))
                },
                f"is_tax_unit_{role}": {YEAR: True},
            }
        if kind == "joint_dependents":
            for j in range(int(rng.integers(1, 4))):
                name = f"child_{i}_{j}"
                members.append(name)
                people[name] = {
                    "age": {YEAR: 5 + j},
                    "is_tax_unit_dependent": {YEAR: True},
                }
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {"members": members, "state_code": {YEAR: "KY"}}
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def run():
    sim = Simulation(situation=_situation())

    def calc(variable):
        return np.asarray(sim.calculate(variable, YEAR), dtype=float)

    out = {
        variable: calc(variable)
        for variable in [
            "ky_modified_agi",
            "ky_modified_agi_if_joint",
            "ky_modified_agi_if_separate",
            "ky_family_size_tax_credit_rate",
            "ky_family_size_tax_credit_rate_if_joint",
            "ky_family_size_tax_credit_rate_if_separate",
            "ky_income_tax_before_refundable_credits",
            "ky_income_tax_before_refundable_credits_if_joint",
            "ky_income_tax_before_refundable_credits_if_separate",
            "adjusted_gross_income_person",
            "ky_agi",
            "is_tax_unit_spouse",
        ]
    }
    out["files_separately"] = np.asarray(sim.calculate("ky_files_separately", YEAR))
    out["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_max(run, values):
    result = np.full(N_RANDOM, -np.inf)
    np.maximum.at(result, run["person_tax_unit"], values)
    return result


def _unit_any(run, values):
    return np.bincount(run["person_tax_unit"], weights=values, minlength=N_RANDOM) > 0


def test_population_exercises_both_paths(run):
    negative = _unit_any(
        run, (run["adjusted_gross_income_person"] < 0) | (run["ky_agi"] < 0)
    )
    assert negative.sum() > 30
    assert run["files_separately"].sum() > 20
    rates_differ = (
        run["ky_family_size_tax_credit_rate_if_separate"]
        != run["ky_family_size_tax_credit_rate_if_joint"]
    )
    assert rates_differ.sum() > 0


def test_negative_income_never_offsets_on_the_separate_path(run):
    separate = run["ky_modified_agi_if_separate"]
    largest_member_agi = _unit_max(
        run, np.maximum(run["adjusted_gross_income_person"], run["ky_agi"])
    )
    assert np.all(separate >= largest_member_agi - TOLERANCE)
    assert np.all(separate >= run["ky_modified_agi_if_joint"] - TOLERANCE)


def test_paths_agree_without_negative_income(run):
    negative = _unit_any(
        run, (run["adjusted_gross_income_person"] < 0) | (run["ky_agi"] < 0)
    )
    np.testing.assert_allclose(
        run["ky_modified_agi_if_separate"][~negative],
        run["ky_modified_agi_if_joint"][~negative],
        atol=TOLERANCE,
    )


def test_separate_rate_never_exceeds_joint_rate(run):
    assert np.all(
        run["ky_family_size_tax_credit_rate_if_separate"]
        <= run["ky_family_size_tax_credit_rate_if_joint"]
    )


def test_elected_values_are_the_elected_paths(run):
    separate = run["files_separately"]
    np.testing.assert_array_equal(
        run["ky_family_size_tax_credit_rate"],
        np.where(
            separate,
            run["ky_family_size_tax_credit_rate_if_separate"],
            run["ky_family_size_tax_credit_rate_if_joint"],
        ),
    )
    np.testing.assert_allclose(
        run["ky_modified_agi"],
        np.where(
            separate,
            run["ky_modified_agi_if_separate"],
            run["ky_modified_agi_if_joint"],
        ),
        atol=TOLERANCE,
    )


def test_post_election_tax_matches_the_elected_path(run):
    joint = run["ky_income_tax_before_refundable_credits_if_joint"]
    separate = run["ky_income_tax_before_refundable_credits_if_separate"]
    tax = run["ky_income_tax_before_refundable_credits"]
    np.testing.assert_allclose(
        tax, np.where(run["files_separately"], separate, joint), atol=TOLERANCE
    )
    married = _unit_any(run, run["is_tax_unit_spouse"])
    np.testing.assert_allclose(
        tax[married], np.minimum(joint, separate)[married], atol=TOLERANCE
    )


@pytest.mark.parametrize("bill, rate", [("hb13", 0.035), ("hb152", 0.04)])
def test_negative_income_credit_composes_with_graduated_tax(bill, rate):
    """Check the bill's gross tax against both credit paths and final liability.

    Federal and Kentucky AGIs agree here, so this does not choose between the
    readings held under d1009. KRS 141.066(4) floors the loss only on the separate
    path; Section 1 of each bill supplies the low-income tax rate.
    """
    year = 2027
    rng = np.random.default_rng(SEED)
    head_income = rng.integers(35_000, 50_001, size=32)
    joint_income = rng.integers(0, 15_001, size=32)
    people, tax_units, households = {}, {}, {}
    for i, (head_agi, joint_agi) in enumerate(zip(head_income, joint_income)):
        members = [f"head_{i}", f"spouse_{i}"]
        for name, role, age, agi, taxable, joint_taxable in (
            (members[0], "head", 45, head_agi, head_agi, joint_agi),
            (members[1], "spouse", 43, joint_agi - head_agi, 0, 0),
        ):
            people[name] = {
                "age": {year: age},
                f"is_tax_unit_{role}": {year: True},
                "adjusted_gross_income_person": {year: int(agi)},
                "ky_agi": {year: int(agi)},
                "ky_taxable_income_indiv": {year: int(taxable)},
                "ky_taxable_income_joint": {year: int(joint_taxable)},
            }
        tax_units[f"tu_{i}"] = {
            "members": members,
            "filing_status": {year: "JOINT"},
        }
        households[f"hh_{i}"] = {
            "members": members,
            "state_code": {year: "KY"},
        }
    parameter_reform = Reform.from_dict(
        {
            f"gov.contrib.states.ky.{bill}.in_effect": {
                "2027-01-01.2027-12-31": True,
            }
        },
        country_id="us",
    )
    sim = Simulation(
        start_instant="2027-01-01",
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        },
    )
    sim.apply_reform((parameter_reform, ky_graduated_income_tax))
    system = sim.tax_benefit_system

    def calc(variable):
        return np.asarray(sim.calculate(variable, year), dtype=float)

    np.testing.assert_allclose(calc("ky_modified_agi_if_joint"), joint_income)
    np.testing.assert_allclose(calc("ky_modified_agi_if_separate"), head_income)
    np.testing.assert_array_equal(calc("ky_family_size_tax_credit_rate_if_joint"), 1)
    np.testing.assert_array_equal(calc("ky_family_size_tax_credit_rate_if_separate"), 0)
    expected_separate_tax = head_income * rate
    np.testing.assert_allclose(
        calc("ky_income_tax_before_refundable_credits_if_separate"),
        expected_separate_tax,
        atol=TOLERANCE,
    )
    np.testing.assert_array_equal(
        calc("ky_income_tax_before_refundable_credits_if_joint"), 0
    )
    np.testing.assert_array_equal(calc("ky_files_separately"), 0)
    np.testing.assert_array_equal(calc("ky_income_tax_before_refundable_credits"), 0)
    # Force the other election to check the post-election credit chain too.
    for tax_unit in tax_units.values():
        tax_unit["ky_files_separately"] = {year: True}
    sim = Simulation(
        tax_benefit_system=system,
        start_instant="2027-01-01",
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        },
    )
    np.testing.assert_allclose(calc("ky_modified_agi"), head_income)
    np.testing.assert_array_equal(calc("ky_family_size_tax_credit_rate"), 0)
    np.testing.assert_allclose(
        calc("ky_income_tax_before_refundable_credits"),
        expected_separate_tax,
        atol=TOLERANCE,
    )
