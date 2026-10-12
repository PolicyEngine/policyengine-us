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
- A role grid of 72 three-adult households: a married couple living with a
  third adult, over all nine assignments of tax-unit head and spouse roles
  among the three adults and aged or not for each adult, plus two-person and
  one-person households in the same simulation. Couple status and SSI must
  not depend on tax roles or on the third adult (416.1801(c), 416.1806,
  416.1160(d)), and joint claims must be symmetric and disjoint from
  ineligible-spouse status.

YAML covers worked cases. Python is needed to check the for-all properties
over every ordered edge of the grids and to compare with an oracle that does
not use the model. Both grids share the read-only system singleton; neither
constructs a model per household. This file routes to the Rest/core group.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
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


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
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
# The same simulation also holds two-person and one-person households, so
# household positions differ across rows.
ADULTS = ("a", "b", "c")
ROLE_ASSIGNMENTS = [
    (head, spouse) for head in ADULTS for spouse in (None, *ADULTS) if spouse != head
]
AGED = (False, True)
INCOME = {"a": 600, "b": 300, "c": 900}


def _adult(age, income, head=False, spouse=False):
    return {
        "age": {YEAR: age},
        "pension_income": {YEAR: 12 * income},
        "is_tax_unit_head": {YEAR: head},
        "is_tax_unit_spouse": {YEAR: spouse},
    }


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

    def add_household(key, people, marital_units):
        situation["people"].update(people)
        for plural in ("tax_units", "households", "families", "spm_units"):
            situation[plural][key] = {"members": list(people)}
        situation["households"][key]["state_code"] = {YEAR: "TX"}
        for index, members in enumerate(marital_units):
            situation["marital_units"][f"{key}_m{index}"] = {"members": members}

    configurations = list(product(product(AGED, repeat=3), ROLE_ASSIGNMENTS))
    for index, (aged, (head, spouse)) in enumerate(configurations):
        names = {adult: f"{adult}{index}" for adult in ADULTS}
        people = {
            names[adult]: _adult(
                70 if is_aged else 50,
                INCOME[adult],
                head=adult == head,
                spouse=adult == spouse,
            )
            for adult, is_aged in zip(ADULTS, aged)
        }
        add_household(f"u{index}", people, [[names["a"], names["b"]], [names["c"]]])
    extras = list(product(AGED, repeat=2))
    for index, (a_aged, b_aged) in enumerate(extras):
        couple = {
            f"pa{index}": _adult(70 if a_aged else 50, INCOME["a"], head=True),
            f"pb{index}": _adult(70 if b_aged else 50, INCOME["b"], spouse=True),
        }
        add_household(f"pair{index}", couple, [list(couple)])
        single = {f"s{index}": _adult(70 if a_aged else 50, INCOME["c"], head=True)}
        add_household(f"single{index}", single, [list(single)])
    return situation, configurations, extras


@pytest.fixture(scope="module")
def role_grid():
    situation, configurations, extras = _role_situation()
    simulation = Simulation(situation=situation)
    grid_people = 3 * len(configurations)
    shape = (len(configurations) // len(ROLE_ASSIGNMENTS), len(ROLE_ASSIGNMENTS), 3)

    def calculate(variable, period):
        values = simulation.calculate(variable, period)
        return values[:grid_people].reshape(shape), values[grid_people:].reshape(
            len(extras), 3
        )

    joint, joint_extra = calculate("ssi_claim_is_joint", YEAR)
    ineligible, ineligible_extra = calculate("is_ssi_ineligible_spouse", YEAR)
    ssi, ssi_extra = calculate("ssi", PERIOD)
    return {
        "aged": [aged for aged, _ in configurations[:: len(ROLE_ASSIGNMENTS)]],
        "joint": joint,
        "ineligible_spouse": ineligible,
        "ssi": ssi,
        "extras": extras,
        "joint_extra": joint_extra,
        "ineligible_extra": ineligible_extra,
        "ssi_extra": ssi_extra,
    }


def test_couple_status_and_ssi_do_not_depend_on_tax_roles(role_grid):
    for name in ("joint", "ineligible_spouse", "ssi"):
        values = role_grid[name]
        assert np.all(values == values[:, :1, :]), name


def test_couple_status_matches_the_couple_definitions(role_grid):
    # 416.1801(c) and 416.1160(d), with aged, blind or disabled status
    # standing for SSI eligibility (ssi_claim_is_joint does not apply the
    # citizenship condition).
    for index, aged in enumerate(role_grid["aged"]):
        couple = aged[0] and aged[1]
        assert np.all(role_grid["joint"][index, :, :2] == couple)
        # The third adult is not married to either spouse.
        assert not np.any(role_grid["joint"][index, :, 2])
        assert not np.any(role_grid["ineligible_spouse"][index, :, 2])
        ineligible = role_grid["ineligible_spouse"][index]
        assert np.all(ineligible[:, 0] == (aged[1] and not aged[0]))
        assert np.all(ineligible[:, 1] == (aged[0] and not aged[1]))
    assert not np.any(role_grid["joint"] & role_grid["ineligible_spouse"])


def test_role_grid_couples_match_the_same_couple_living_alone(role_grid):
    # Columns are (pair a, pair b, single). A couple's status and SSI do not
    # change when a third adult shares their household and tax unit.
    joint_extra = role_grid["joint_extra"]
    ssi_extra = role_grid["ssi_extra"]
    for index, (a_aged, b_aged) in enumerate(role_grid["extras"]):
        assert np.all(joint_extra[index, :2] == (a_aged and b_aged))
        assert not joint_extra[index, 2]
        assert not role_grid["ineligible_extra"][index, 2]
        rows = [
            row
            for row, aged in enumerate(role_grid["aged"])
            if aged[:2] == (a_aged, b_aged)
        ]
        for row in rows:
            np.testing.assert_allclose(
                role_grid["ssi"][row, 0, :2], ssi_extra[index, :2], atol=0.01
            )
