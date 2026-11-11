"""Invariants for Delaware's exclusion for people 60 or older or disabled.

30 Del. C. 1106(b)(2) and the PIT-RES line 11 worksheet test a joint return as
a couple: both spouses 60 or older or totally and permanently disabled,
combined earned income under $5,000 and joint line 10 of $20,000 or less, for
$4,000 (each spouse's column in the model gets half). Other returns, including
spouses' separate columns, test each filer against $2,500 and $10,000 for
$2,000.

The properties must hold for every tax unit, so the tests draw a seeded random
population of Delaware tax units (joint couples with and without dependents,
and single filers) with low wages, pensions and disability, near the limits,
and run it as one vectorized simulation:

1. Dependents get no exclusion. On a joint return the head and spouse get the
   same amount, either nothing or $2,000 each.
2. Necessary conditions: a joint couple with a spouse under 60 and not
   disabled, combined earned income of $5,000 or more, or joint line 10 over
   $20,000 gets nothing.
3. The joint test is no stricter than the individual test: if both spouses
   would pass it on their own, the couple qualifies.
4. Returns other than joint ones get the individual exclusion.
5. Only the couple's totals matter on a joint return: moving one spouse's wages
   to the other, which keeps combined earned income and line 10, never changes
   the exclusion.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
N_RANDOM = 200
SEED = 20261006
AGE_THRESHOLD = 60
JOINT_EARNED_INCOME_LIMIT = 5_000
JOINT_LINE_10_LIMIT = 20_000


def _adult(rng, role):
    return {
        "age": {
            YEAR: int(
                rng.integers(45, 60) if rng.random() < 0.2 else rng.integers(60, 85)
            )
        },
        "is_disabled": {YEAR: bool(rng.random() < 0.15)},
        "employment_income": {
            YEAR: float(round(rng.choice([0.0, rng.uniform(0, 4_500)])))
        },
        "taxable_pension_income": {
            YEAR: float(round(rng.choice([0.0, 0.0, rng.uniform(0, 20_000)])))
        },
        f"is_tax_unit_{role}": {YEAR: True},
    }


def _situation(pool_wages=False):
    rng = np.random.default_rng(SEED)
    people, tax_units, households = {}, {}, {}
    for i in range(N_RANDOM):
        kind = rng.choice(["single", "joint", "joint", "joint_dependents"])
        roles = ["head"] if kind == "single" else ["head", "spouse"]
        members = []
        for role in roles:
            name = f"{role}_{i}"
            members.append(name)
            people[name] = _adult(rng, role)
        if pool_wages and kind != "single":
            head, spouse = people[f"head_{i}"], people[f"spouse_{i}"]
            head["employment_income"][YEAR] += spouse["employment_income"][YEAR]
            spouse["employment_income"][YEAR] = 0.0
        if kind == "joint_dependents":
            name = f"child_{i}"
            members.append(name)
            people[name] = {"age": {YEAR: 15}, "is_tax_unit_dependent": {YEAR: True}}
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {"members": members, "state_code": {YEAR: "DE"}}
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def run():
    sim = Simulation(situation=_situation())

    def calc(variable):
        return np.asarray(sim.calculate(variable, YEAR))

    out = {
        variable: calc(variable)
        for variable in [
            "de_elderly_or_disabled_income_exclusion_joint",
            "de_elderly_or_disabled_income_exclusion_indiv",
            "de_elderly_or_disabled_income_exclusion_eligible_person",
            "de_pre_exclusions_agi",
            "earned_income",
            "age",
            "is_disabled",
            "is_tax_unit_head",
            "is_tax_unit_spouse",
            "is_tax_unit_dependent",
        ]
    }
    filing_status = sim.calculate("filing_status", YEAR).decode_to_str()
    out["joint"] = filing_status == "JOINT"
    out["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    pooled = Simulation(situation=_situation(pool_wages=True))
    out["pooled_exclusion"] = np.asarray(
        pooled.calculate("de_elderly_or_disabled_income_exclusion_joint", YEAR)
    )
    out["pooled_earned_income"] = np.asarray(pooled.calculate("earned_income", YEAR))
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["person_tax_unit"], weights=values, minlength=len(run["joint"])
    )


def _joint_person(run):
    return run["joint"][run["person_tax_unit"]]


def _filer(run):
    return run["is_tax_unit_head"] | run["is_tax_unit_spouse"]


def test_population_reaches_both_outcomes(run):
    exclusion = run["de_elderly_or_disabled_income_exclusion_joint"]
    joint_units = _unit_sum(run, exclusion) * run["joint"]
    assert (joint_units == 4_000).sum() > 10
    assert ((joint_units == 0) & run["joint"]).sum() > 50


def test_joint_return_gets_nothing_or_2000_per_spouse(run):
    exclusion = run["de_elderly_or_disabled_income_exclusion_joint"]
    assert np.all(exclusion[run["is_tax_unit_dependent"]] == 0)
    joint_filer = _joint_person(run) & _filer(run)
    assert np.isin(exclusion[joint_filer], [0, 2_000]).all()
    unit_total = _unit_sum(run, exclusion)
    assert np.isin(unit_total[run["joint"]], [0, 4_000]).all()


def test_joint_return_meets_each_condition(run):
    exclusion = run["de_elderly_or_disabled_income_exclusion_joint"]
    filer = _filer(run)
    age_or_disabled = (run["age"] >= AGE_THRESHOLD) | run["is_disabled"]
    both_qualify = _unit_sum(run, filer & age_or_disabled) == 2
    combined_earned = _unit_sum(run, filer * run["earned_income"])
    line_10 = _unit_sum(run, run["de_pre_exclusions_agi"])
    granted = _unit_sum(run, exclusion) > 0
    joint = run["joint"]
    assert not (granted & joint & ~both_qualify).any()
    assert not (granted & joint & (combined_earned >= JOINT_EARNED_INCOME_LIMIT)).any()
    assert not (granted & joint & (line_10 > JOINT_LINE_10_LIMIT)).any()


def test_joint_test_is_no_stricter_than_both_individual_tests(run):
    filer = _filer(run)
    eligible = run["de_elderly_or_disabled_income_exclusion_eligible_person"]
    both_individually = _unit_sum(run, filer & eligible) == 2
    granted = _unit_sum(run, run["de_elderly_or_disabled_income_exclusion_joint"]) > 0
    assert (both_individually & run["joint"]).sum() > 0
    assert granted[both_individually & run["joint"]].all()


def test_other_returns_use_the_individual_test(run):
    other = ~_joint_person(run)
    np.testing.assert_array_equal(
        run["de_elderly_or_disabled_income_exclusion_joint"][other],
        run["de_elderly_or_disabled_income_exclusion_indiv"][other],
    )


def test_joint_exclusion_depends_only_on_the_couples_totals(run):
    joint = _joint_person(run)
    # Couples that qualify after pooling though one spouse's pooled wages are
    # over the $2,500 individual limit.
    over_individual_limit = run["pooled_earned_income"] >= 2_500
    granted_over_limit = _unit_sum(
        run, (run["pooled_exclusion"] > 0) & over_individual_limit
    )
    assert (granted_over_limit > 0).sum() > 5
    exclusion = run["de_elderly_or_disabled_income_exclusion_joint"]
    pooled = run["pooled_exclusion"]
    np.testing.assert_array_equal(exclusion[joint], pooled[joint])
