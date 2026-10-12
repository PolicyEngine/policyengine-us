"""Simulation-API invariants for SSI couples and spousal deeming.

Two vectorized simulations, each built once per module:

- An income grid of 400 two-person households: an aged claimant with only
  unearned income and a spouse under 65 with unearned and earned income. The
  axes include the $20 and $65 exclusion edges, the $497 deeming threshold
  ($1,491 couple less $994 individual Federal benefit rate in 2026) and its
  neighbours, and a claimant income that leaves nothing of the individual
  rate. SSI must equal an independent numpy reading of 20 CFR 416.1163, never
  exceed the benefit without deeming (416.1163(e)(2)), and never rise when any
  income rises.
- A role grid of 144 three-adult households: a married couple living with a
  third adult, over all nine assignments of tax-unit head and spouse roles
  among the three adults, aged or not for each adult, and citizen or
  undocumented for one spouse. Couple status and SSI must not depend on tax roles
  (416.1801(c), 416.1806, 416.1160(d)), and joint claims must be symmetric and
  disjoint from ineligible-spouse status.

YAML covers worked cases. Python is needed to check the for-all properties
over every ordered edge of the grids and to compare with an oracle that does
not use the model. Both grids share the read-only system singleton; neither
constructs a model per household. This file routes to the Rest/core group.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
PERIOD = "2026-01"
INDIVIDUAL_FBR = 994
COUPLE_FBR = 1_491
GENERAL_EXCLUSION = 20
EARNED_EXCLUSION = 65

CLAIMANT_UNEARNED = (0, 19, 20, 400, 743, 974, 1_014, 1_200)
SPOUSE_UNEARNED = (0, 100, 300, 497, 498)
SPOUSE_EARNED = (0, 64, 65, 400, 496, 497, 498, 600, 1_000, 3_100)


def _countable(unearned, earned):
    """416.1112, 416.1124: $20 general, then $65 and half of the rest."""
    general = np.minimum(GENERAL_EXCLUSION, unearned)
    leftover = GENERAL_EXCLUSION - general
    earned_after = np.maximum(earned - EARNED_EXCLUSION - leftover, 0) / 2
    return unearned - general + earned_after


def _oracle_ssi(claimant_unearned, spouse_unearned, spouse_earned):
    """Monthly SSI for an aged claimant with an ineligible spouse.

    416.1163(d)(1): no deeming when the spouse's income is not more than the
    couple rate less the individual rate. (d)(2): otherwise the couple's
    combined countable income is subtracted from the couple rate. (e)(2): the
    benefit is the lesser of that and the individual rate less the claimant's
    own countable income.
    """
    alone = np.maximum(
        INDIVIDUAL_FBR
        - _countable(claimant_unearned, np.zeros_like(claimant_unearned)),
        0,
    )
    couple = np.maximum(
        COUPLE_FBR - _countable(claimant_unearned + spouse_unearned, spouse_earned),
        0,
    )
    deems = spouse_unearned + spouse_earned > COUPLE_FBR - INDIVIDUAL_FBR
    return np.where(deems, np.minimum(couple, alone), alone)


def _income_situation(rows):
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    for index, (claimant_unearned, spouse_unearned, spouse_earned) in enumerate(rows):
        claimant, spouse = f"c{index}", f"s{index}"
        situation["people"][claimant] = {
            "age": {YEAR: 70},
            "pension_income": {YEAR: 12 * claimant_unearned},
        }
        situation["people"][spouse] = {
            "age": {YEAR: 60},
            "pension_income": {YEAR: 12 * spouse_unearned},
            "employment_income": {YEAR: 12 * spouse_earned},
        }
        members = [claimant, spouse]
        for plural in (
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        ):
            situation[plural][f"u{index}"] = {"members": members}
        situation["households"][f"u{index}"]["state_code"] = {YEAR: "TX"}
    return situation


def _income_ssi(rows):
    simulation = Simulation(situation=_income_situation(rows))
    ssi = simulation.calculate("ssi", PERIOD)
    without_deeming = simulation.calculate(
        "uncapped_ssi_without_spousal_deeming", PERIOD
    )
    return ssi[0::2], ssi[1::2], np.maximum(without_deeming[0::2], 0)


@pytest.fixture(scope="module")
def income_grid():
    rows = list(product(CLAIMANT_UNEARNED, SPOUSE_UNEARNED, SPOUSE_EARNED))
    claimant_ssi, spouse_ssi, without_deeming = _income_ssi(rows)
    shape = (len(CLAIMANT_UNEARNED), len(SPOUSE_UNEARNED), len(SPOUSE_EARNED))
    columns = np.array(rows, dtype=float).T
    return {
        "rows": columns,
        "ssi": claimant_ssi.reshape(shape),
        "spouse_ssi": spouse_ssi,
        "without_deeming": without_deeming.reshape(shape),
        "oracle": _oracle_ssi(*columns).reshape(shape),
    }


def test_income_grid_matches_independent_oracle(income_grid):
    np.testing.assert_allclose(income_grid["ssi"], income_grid["oracle"], atol=0.01)
    assert np.all(income_grid["spouse_ssi"] == 0)


def test_deemed_benefit_never_exceeds_benefit_without_deeming(income_grid):
    assert np.all(income_grid["ssi"] <= income_grid["without_deeming"] + 0.01)


@pytest.mark.parametrize("axis", [0, 1, 2], ids=["claimant", "unearned", "earned"])
def test_ssi_never_rises_with_income(income_grid, axis):
    # Each axis is sorted ascending, so every ordered edge is a rise in one
    # income with the others fixed.
    assert np.all(np.diff(income_grid["ssi"], axis=axis) <= 0.01)


@settings(max_examples=3, deadline=None, derandomize=True)
@given(
    st.lists(
        st.tuples(
            st.integers(0, 1_300),
            st.integers(0, 900),
            st.integers(0, 3_500),
        ),
        min_size=40,
        max_size=40,
    )
)
def test_random_incomes_match_independent_oracle(rows):
    claimant_ssi, _, _ = _income_ssi(rows)
    expected = _oracle_ssi(*np.array(rows, dtype=float).T)
    np.testing.assert_allclose(claimant_ssi, expected, atol=0.01)


# Role grid: adults "a" and "b" are married; "c" lives with them in its own
# marital unit. Every head/spouse assignment among the three is supplied.
ADULTS = ("a", "b", "c")
ROLE_ASSIGNMENTS = [
    (head, spouse) for head in ADULTS for spouse in (None, *ADULTS) if spouse != head
]
AGED = (False, True)
B_STATUS = ("CITIZEN", "UNDOCUMENTED")


def _role_situation():
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    configurations = []
    income = {"a": 600, "b": 300, "c": 900}
    for index, (aged, status, roles) in enumerate(
        product(product(AGED, repeat=3), B_STATUS, ROLE_ASSIGNMENTS)
    ):
        head, spouse = roles
        names = {adult: f"{adult}{index}" for adult in ADULTS}
        for adult, is_aged in zip(ADULTS, aged):
            person = {
                "age": {YEAR: 70 if is_aged else 50},
                "pension_income": {YEAR: 12 * income[adult]},
                "is_tax_unit_head": {YEAR: adult == head},
                "is_tax_unit_spouse": {YEAR: adult == spouse},
            }
            if adult == "b":
                person["immigration_status"] = {YEAR: status}
            situation["people"][names[adult]] = person
        members = list(names.values())
        for plural in ("tax_units", "households", "families", "spm_units"):
            situation[plural][f"u{index}"] = {"members": members}
        situation["households"][f"u{index}"]["state_code"] = {YEAR: "TX"}
        situation["marital_units"][f"couple{index}"] = {
            "members": [names["a"], names["b"]]
        }
        situation["marital_units"][f"single{index}"] = {"members": [names["c"]]}
        configurations.append((aged, status))
    return situation, configurations


@pytest.fixture(scope="module")
def role_grid():
    situation, configurations = _role_situation()
    simulation = Simulation(situation=situation)
    shape = (len(configurations) // len(ROLE_ASSIGNMENTS), len(ROLE_ASSIGNMENTS), 3)

    def calculate(variable, period):
        return simulation.calculate(variable, period).reshape(shape)

    return {
        "configurations": configurations[:: len(ROLE_ASSIGNMENTS)],
        "joint": calculate("ssi_claim_is_joint", YEAR),
        "ineligible_spouse": calculate("is_ssi_ineligible_spouse", YEAR),
        "ssi": calculate("ssi", PERIOD),
    }


def test_couple_status_and_ssi_do_not_depend_on_tax_roles(role_grid):
    for name in ("joint", "ineligible_spouse", "ssi"):
        values = role_grid[name]
        assert np.all(values == values[:, :1, :]), name


def test_joint_claims_follow_the_eligible_couple_definition(role_grid):
    joint = role_grid["joint"]
    ineligible_spouse = role_grid["ineligible_spouse"]
    for index, (aged, status) in enumerate(role_grid["configurations"]):
        a_eligible = aged[0]
        b_eligible = aged[1] and status == "CITIZEN"
        couple = a_eligible and b_eligible
        assert np.all(joint[index, :, 0] == couple)
        assert np.all(joint[index, :, 1] == couple)
        # The third adult is not married to either spouse.
        assert not np.any(joint[index, :, 2])
        assert not np.any(ineligible_spouse[index, :, 2])
        assert np.all(ineligible_spouse[index, :, 0] == (b_eligible and not a_eligible))
        assert np.all(ineligible_spouse[index, :, 1] == (a_eligible and not b_eligible))
    assert not np.any(joint & ineligible_spouse)
