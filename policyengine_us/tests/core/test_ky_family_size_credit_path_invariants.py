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

1. Negative federal AGI attributed for Kentucky or Kentucky AGI never offsets
   another member's income on the combined-separate path: its modified gross
   income is at least every member's federal and Kentucky AGI and the joint
   amount. With no negative member, the two paths agree.
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
def population():
    # Keep the original 200 random tax units unchanged and append the focused
    # ownership population. Both properties are read-only, so one model setup
    # exercises both without sharing mutable reform or election state.
    situation = _situation()
    ownership_situation, expected = _ownership_situation()
    for entity, units in ownership_situation.items():
        situation[entity].update(units)
    return Simulation(situation=situation), expected


@pytest.fixture(scope="module")
def run(population):
    sim, _ = population
    person_tax_unit = sim.populations["tax_unit"].members_entity_id
    original_people = person_tax_unit < N_RANDOM

    def calc(variable):
        values = np.asarray(sim.calculate(variable, YEAR), dtype=float)
        if sim.tax_benefit_system.variables[variable].entity.key == "person":
            return values[original_people]
        return values[:N_RANDOM]

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
            "ky_federal_agi",
            "ky_agi",
            "is_tax_unit_spouse",
        ]
    }
    out["files_separately"] = np.asarray(sim.calculate("ky_files_separately", YEAR))[
        :N_RANDOM
    ]
    out["person_tax_unit"] = person_tax_unit[original_people]
    return out


def _unit_max(run, values):
    result = np.full(N_RANDOM, -np.inf)
    np.maximum.at(result, run["person_tax_unit"], values)
    return result


def _unit_any(run, values):
    return np.bincount(run["person_tax_unit"], weights=values, minlength=N_RANDOM) > 0


def test_population_exercises_both_paths(run):
    negative = _unit_any(run, (run["ky_federal_agi"] < 0) | (run["ky_agi"] < 0))
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
        run, np.maximum(run["ky_federal_agi"], run["ky_agi"])
    )
    assert np.all(separate >= largest_member_agi - TOLERANCE)
    assert np.all(separate >= run["ky_modified_agi_if_joint"] - TOLERANCE)


def test_paths_agree_without_negative_income(run):
    negative = _unit_any(run, (run["ky_federal_agi"] < 0) | (run["ky_agi"] < 0))
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


def _ownership_situation():
    rng = np.random.default_rng(SEED)
    sources = (
        "self_employment_income",
        "farm_operations_income",
        "rental_income",
        "farm_rent_income",
        "estate_income",
        "partnership_s_corp_income",
    )
    people, tax_units, households = {}, {}, {}
    expected_people, expected_separate, expected_joint = [], [], []
    for source in sources:
        for scenario in range(8):
            wages = int(rng.integers(35_000, 60_001))
            # Half exercise uncapped losses; half exceed the joint-return cap.
            loss = int(rng.integers(20_000, 80_001))
            if scenario % 2:
                loss += 626_000
            allowed_loss = min(loss, 626_000)
            for wage_owner in ("head", "spouse"):
                i = len(tax_units)
                members = [f"loss_head_{i}", f"loss_spouse_{i}"]
                for name, role in zip(members, ("head", "spouse")):
                    owns_wages = role == wage_owner
                    people[name] = {
                        "age": {YEAR: 45},
                        f"is_tax_unit_{role}": {YEAR: True},
                        "employment_income": {YEAR: wages if owns_wages else 0},
                        source: {YEAR: 0 if owns_wages else -loss},
                    }
                    expected_people.append(wages if owns_wages else -allowed_loss)
                tax_units[f"loss_tu_{i}"] = {
                    "members": members,
                    "filing_status": {YEAR: "JOINT"},
                }
                households[f"loss_hh_{i}"] = {
                    "members": members,
                    "state_code": {YEAR: "KY"},
                }
                expected_separate.append(wages)
                expected_joint.append(wages - allowed_loss)
    return (
        {"people": people, "tax_units": tax_units, "households": households},
        (expected_people, expected_separate, expected_joint),
    )


def test_leaf_losses_stay_with_their_owner_and_conserve_joint_agi(population):
    """An independent leaf oracle detects losses hidden by shared federal AGI.

    For each modeled business/rental source, swap which spouse earns wages and
    which owns the loss. An owner's loss cannot reduce the other spouse's
    separately computed income. Attribution preserves the joint federal AGI
    and the Section 461(l) cap (the 2025 joint-return threshold is $626,000).
    These checks require Python to compare a generated vector population to
    an independent oracle and to each ownership-swapped observation.
    """
    sim, (expected_people, expected_separate, expected_joint) = population
    ownership_people = sim.populations["tax_unit"].members_entity_id >= N_RANDOM

    def calc(variable):
        values = sim.calculate(variable, YEAR)
        if sim.tax_benefit_system.variables[variable].entity.key == "person":
            return values[ownership_people]
        return values[N_RANDOM:]

    # Existing outputs come first so the regression fails economically at the
    # old head, rather than failing because the new attribution variable is absent.
    np.testing.assert_allclose(calc("ky_agi"), expected_people, atol=TOLERANCE)
    separate = calc("ky_modified_agi_if_separate")
    np.testing.assert_allclose(separate, expected_separate, atol=TOLERANCE)
    np.testing.assert_allclose(separate[::2], separate[1::2], atol=TOLERANCE)
    np.testing.assert_allclose(
        calc("ky_modified_agi_if_joint"),
        expected_joint,
        atol=TOLERANCE,
    )
    federal = calc("adjusted_gross_income_person").reshape(-1, 2)
    attributed = calc("ky_federal_agi").reshape(-1, 2)
    np.testing.assert_allclose(attributed.reshape(-1), expected_people, atol=TOLERANCE)
    np.testing.assert_allclose(federal.sum(axis=1), expected_joint, atol=TOLERANCE)
    np.testing.assert_allclose(
        attributed.sum(axis=1), federal.sum(axis=1), atol=TOLERANCE
    )


@pytest.mark.parametrize("bill, rate", [("hb13", 0.035), ("hb152", 0.04)])
def test_negative_income_credit_composes_with_graduated_tax(bill, rate):
    """Check both credit paths and liability from wages and business losses.

    Federal and Kentucky AGIs agree here, so this does not choose between the
    readings held under d1009. KRS 141.066(4) floors the loss only on the separate
    path; Section 1 of each bill supplies the tax rates. The final observation
    has separate taxable income above $250,000, where HB 13 differs from the
    baseline 3.5% rate, so dropping the structural reform cannot pass.
    """
    year = 2027
    rng = np.random.default_rng(SEED)
    head_income = np.append(rng.integers(35_000, 50_001, size=32), 350_000)
    joint_income = np.append(rng.integers(0, 15_001, size=32), 10_000)
    people, tax_units, households = {}, {}, {}
    for i, (wages, combined_income) in enumerate(zip(head_income, joint_income)):
        members = [f"head_{i}", f"spouse_{i}"]
        people[members[0]] = {
            "age": {year: 45},
            "is_tax_unit_head": {year: True},
            "employment_income": {year: int(wages)},
        }
        people[members[1]] = {
            "age": {year: 43},
            "is_tax_unit_spouse": {year: True},
            "self_employment_income": {year: int(combined_income - wages)},
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
    standard = system.parameters(
        "2027-01-01"
    ).gov.states.ky.tax.income.deductions.standard

    def calc(simulation, variable):
        return np.asarray(simulation.calculate(variable, year), dtype=float)

    np.testing.assert_allclose(calc(sim, "ky_modified_agi_if_joint"), joint_income)
    np.testing.assert_allclose(calc(sim, "ky_modified_agi_if_separate"), head_income)
    np.testing.assert_array_equal(
        calc(sim, "ky_family_size_tax_credit_rate_if_joint"), 1
    )
    np.testing.assert_array_equal(
        calc(sim, "ky_family_size_tax_credit_rate_if_separate"), 0
    )
    separate_taxable = np.maximum(head_income - standard, 0)
    # Both bills apply 6% to the full income at this observation's cliff.
    expected_separate_tax = separate_taxable * np.append(np.full(32, rate), 0.06)
    np.testing.assert_allclose(
        calc(sim, "ky_income_tax_before_refundable_credits_if_separate"),
        expected_separate_tax,
        atol=TOLERANCE,
    )
    np.testing.assert_array_equal(
        calc(sim, "ky_income_tax_before_refundable_credits_if_joint"), 0
    )
    np.testing.assert_array_equal(calc(sim, "ky_files_separately"), 0)
    np.testing.assert_array_equal(
        calc(sim, "ky_income_tax_before_refundable_credits"), 0
    )
    # Force the other election to check the post-election credit chain too.
    for tax_unit in tax_units.values():
        tax_unit["ky_files_separately"] = {year: True}
    forced_sim = Simulation(
        tax_benefit_system=system,
        start_instant="2027-01-01",
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        },
    )
    np.testing.assert_allclose(calc(forced_sim, "ky_modified_agi"), head_income)
    np.testing.assert_array_equal(calc(forced_sim, "ky_family_size_tax_credit_rate"), 0)
    np.testing.assert_allclose(
        calc(forced_sim, "ky_income_tax_before_refundable_credits"),
        expected_separate_tax,
        atol=TOLERANCE,
    )
