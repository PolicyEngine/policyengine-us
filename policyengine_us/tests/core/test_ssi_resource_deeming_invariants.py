"""Simulation-API invariants for SSI resource deeming (20 CFR 416.1202/1205).

The complete seven-point Cartesian grids cover single applicants, eligible
couples, applicants with an ineligible spouse, and children with one or two
parents. Each coordinate is one person's resource stock. Seven points include
both federal limits, the individual limit's immediate neighbors, the couple
limit's upper neighbor, zero, and a value above the reformed couple limit.
Another 81 four-axis households exercise sibling reallocation. All 578
independent households (1,654 people) share one vectorized simulation per
policy: baseline and $10,000/$20,000 limits.

The grids keep household relationships fixed. Household membership represents
coresidence, including retained membership during a temporary absence under
20 CFR 416.1167.

YAML covers the source examples. Python is needed here to compare a frozen
prechange formula, check every ordered edge of each Cartesian grid, and compare
independent resource-test oracles using the Simulation API. Those oracles fail
if either deemed-resource formula is removed. A single module fixture builds
two independent simulation caches from the read-only system singleton; it never
constructs a model per grid point. This file routes to the existing Rest/core
Python group in Makefile. Local elapsed time and peak RSS must be reported after
the test run; there is no claim that a local measurement represents Linux CI
cost.
"""

from copy import deepcopy
from itertools import product

import numpy as np
import pytest

from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform
from policyengine_us import Simulation
from policyengine_us.system import system


YEAR = 2026
PERIOD = "2026-01"
RESOURCES = (0, 1_999, 2_000, 2_001, 3_000, 3_001, 20_001)
DIMENSIONS = {
    "single": 1,
    "joint": 2,
    "spouse": 2,
    "one_parent": 2,
    "two_parents": 3,
}
CASE_GRIDS = {
    kind: (RESOURCES,) * dimensions for kind, dimensions in DIMENSIONS.items()
}
# Own resources, parent resources, parent-spouse resources, sibling resources.
# The 225/1500/4800 combination is the Goode reallocation example in
# POMS SI 01330.280: sibling2400 fails, then claimant2025 fails.
CASE_GRIDS["two_children"] = (
    (0, 225, 2_001),
    (0, 3_000, 4_800),
    (0, 1_000, 3_001),
    (0, 500, 1_500),
)
GRID_SHAPES = {
    kind: tuple(len(axis) for axis in axes) for kind, axes in CASE_GRIDS.items()
}
GRID_SHAPES["two_children_sibling"] = GRID_SHAPES["two_children"]


class HigherSSIResourceLimits(Reform):
    def apply(self):
        def modifier(parameters):
            limits = parameters.gov.ssa.ssi.eligibility.resources.limit
            active = make_period(f"year:{YEAR}:10")
            limits.individual.update(period=active, value=10_000)
            limits.couple.update(period=active, value=20_000)
            return parameters

        self.modify_parameters(modifier)


def _situation():
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
    claimant_positions = {kind: [] for kind in GRID_SHAPES}
    no_deemor_positions = []
    frozen_own = []
    frozen_joint = []
    frozen_marital_group = []
    marital_group_index = 0
    for kind, axes in CASE_GRIDS.items():
        for case_index, amounts in enumerate(product(*axes)):
            prefix = f"{kind}_{case_index}"
            child_case = kind in ("one_parent", "two_parents", "two_children")
            if child_case:
                roles = ["parent"]
                if kind in ("two_parents", "two_children"):
                    roles.append("parent_spouse")
                roles.append("child")
                amount_by_role = dict(zip(["child", *roles[:-1]], amounts))
                if kind == "two_children":
                    roles.append("sibling")
                    amount_by_role["sibling"] = amounts[-1]
                claimant_role = "child"
            else:
                roles = ["head"] + ([] if kind == "single" else ["spouse"])
                amount_by_role = dict(zip(roles, amounts))
                claimant_role = "head"
            members = [f"{prefix}_{role}" for role in roles]
            for role, member in zip(roles, members):
                position = len(situation["people"])
                is_child = role in ("child", "sibling")
                is_head = role in ("head", "parent")
                is_spouse = role in ("spouse", "parent_spouse")
                abd = is_child or role == "head" or (kind == "joint")
                situation["people"][member] = {
                    "age": {YEAR: 10 if is_child else 40},
                    "is_ssi_aged_blind_disabled": {YEAR: abd},
                    "is_parent": {YEAR: role in ("parent", "parent_spouse")},
                    "is_tax_unit_head": {YEAR: is_head},
                    "is_tax_unit_spouse": {YEAR: is_spouse},
                    "is_tax_unit_dependent": {YEAR: is_child},
                    "is_household_head": {YEAR: is_head},
                    "ssi_countable_resources": {YEAR: amount_by_role[role]},
                }
                frozen_own.append(amount_by_role[role])
                frozen_joint.append(kind == "joint")
                frozen_marital_group.append(
                    marital_group_index
                    + (2 if role == "sibling" else 1 if is_child else 0)
                )
                if role == claimant_role:
                    claimant_positions[kind].append(position)
                if role == "sibling":
                    claimant_positions["two_children_sibling"].append(position)
                if kind in ("single", "joint"):
                    no_deemor_positions.append(position)
            for plural in ("tax_units", "households", "families", "spm_units"):
                situation[plural][prefix] = {"members": members}
            if child_case:
                child_count = 2 if kind == "two_children" else 1
                situation["marital_units"][f"{prefix}_parents"] = {
                    "members": members[:-child_count]
                }
                for child_index, member in enumerate(members[-child_count:]):
                    situation["marital_units"][f"{prefix}_child_{child_index}"] = {
                        "members": [member]
                    }
                marital_group_index += 1 + child_count
            else:
                situation["marital_units"][prefix] = {"members": members}
                marital_group_index += 1
    frozen = {
        "own": np.array(frozen_own, dtype=float),
        "joint": np.array(frozen_joint, dtype=bool),
        "marital_group": np.array(frozen_marital_group),
        "no_deemor": np.array(no_deemor_positions),
    }
    return situation, claimant_positions, frozen


def _frozen_old_formula(frozen, individual_limit, couple_limit):
    """Exact numpy translation of the formula frozen at commit 00968dee79.

    countable = where(joint_claim, marital_unit.sum(own), own)
    limit = where(joint_claim, couple, individual)
    return countable <= limit

    The inputs are constructed independently of the new deemed-resource
    formulas. No current deeming output enters this reference calculation.
    """
    marital_totals = np.bincount(frozen["marital_group"], weights=frozen["own"])
    countable = np.where(
        frozen["joint"],
        marital_totals[frozen["marital_group"]],
        frozen["own"],
    )
    limits = np.where(frozen["joint"], couple_limit, individual_limit)
    return countable <= limits


def _redistributed_child_passes(own_resources, parental_excess, individual_limit):
    """Independent SI 01330.200 B equal-division eligibility calculation.

    Start with children whose own resources pass. Repeatedly divide the excess
    among the remaining children and remove every child who fails that share.
    This oracle needs neither a deeming amount nor the model's entity helpers.
    """
    own_resources = np.asarray(own_resources, dtype=float)
    eligible = own_resources <= individual_limit
    while np.any(eligible):
        share = parental_excess / np.count_nonzero(eligible)
        remaining = eligible & (own_resources + share <= individual_limit)
        if np.array_equal(remaining, eligible):
            break
        eligible = remaining
    return eligible


def _resource_test_oracles(individual_limit, couple_limit):
    """Closed-form references built only from the resource coordinates/limits."""
    expected = {}
    own, spouse = np.meshgrid(*CASE_GRIDS["spouse"], indexing="ij")
    expected["spouse"] = own + spouse <= couple_limit
    for kind, allowance in (
        ("one_parent", individual_limit),
        ("two_parents", couple_limit),
    ):
        own, *parents = np.meshgrid(*CASE_GRIDS[kind], indexing="ij")
        parental_excess = np.maximum(0, np.sum(parents, axis=0) - allowance)
        expected[kind] = own + parental_excess <= individual_limit

    children = []
    for own, parent, parent_spouse, sibling in product(*CASE_GRIDS["two_children"]):
        children.append(
            _redistributed_child_passes(
                [own, sibling],
                max(0, parent + parent_spouse - couple_limit),
                individual_limit,
            )
        )
    children = np.asarray(children)
    expected["two_children"] = children[:, 0].reshape(GRID_SHAPES["two_children"])
    expected["two_children_sibling"] = children[:, 1].reshape(
        GRID_SHAPES["two_children_sibling"]
    )
    return expected


@pytest.fixture(scope="module")
def resource_grids():
    situation, positions, frozen = _situation()
    policies = (system, HigherSSIResourceLimits(system))
    snapshots = []
    for policy in policies:
        simulation = Simulation(
            tax_benefit_system=policy, situation=deepcopy(situation)
        )
        passes = np.asarray(simulation.calculate("meets_ssi_resource_test", PERIOD))
        limits = policy.parameters(PERIOD).gov.ssa.ssi.eligibility.resources.limit
        snapshots.append(
            {
                "passes": passes,
                "limits": (limits.individual, limits.couple),
                "grids": {
                    kind: passes[indices].reshape(GRID_SHAPES[kind])
                    for kind, indices in positions.items()
                },
                "deemed": {
                    name: np.asarray(simulation.calculate(name, PERIOD))
                    for name in (
                        "ssi_resources_for_deeming",
                        "ssi_resources_deemed_from_ineligible_spouse",
                        "ssi_resources_deemed_from_ineligible_parent",
                    )
                },
                "old": _frozen_old_formula(frozen, limits.individual, limits.couple),
            }
        )
        # Only immutable result arrays survive; each policy has its own cache.
        del simulation
    return snapshots, frozen["no_deemor"]


def test_no_deemor_matches_frozen_old_formula(resource_grids):
    snapshots, no_deemor = resource_grids
    for snapshot in snapshots:
        np.testing.assert_array_equal(
            snapshot["passes"][no_deemor], snapshot["old"][no_deemor]
        )


def test_resource_grids_match_independent_oracles(resource_grids):
    snapshots, _ = resource_grids
    for snapshot in snapshots:
        for kind, expected in _resource_test_oracles(*snapshot["limits"]).items():
            np.testing.assert_array_equal(
                snapshot["grids"][kind], expected, err_msg=kind
            )


def test_resource_and_limit_monotonicity(resource_grids):
    snapshots, _ = resource_grids
    for snapshot in snapshots:
        for kind, grid in snapshot["grids"].items():
            # Every adjacent ordered resource value, along every resident's
            # resource axis, must preserve a failure. Adjacent comparisons
            # imply the property for every larger value in the finite grid.
            for axis in range(grid.ndim):
                assert np.all(np.diff(grid.astype(int), axis=axis) <= 0), (
                    kind,
                    axis,
                )
    baseline, higher_limits = snapshots
    assert np.all(~baseline["passes"] | higher_limits["passes"])
    # Ensure the grids exercise both outcomes and a real reform transition.
    assert np.any(baseline["passes"]) and np.any(~baseline["passes"])
    assert np.any(baseline["passes"] != higher_limits["passes"])
    assert np.any(~higher_limits["passes"])


def test_deemed_resources_are_nonnegative(resource_grids):
    snapshots, _ = resource_grids
    for snapshot in snapshots:
        for name, amounts in snapshot["deemed"].items():
            assert np.all(np.isfinite(amounts)), name
            assert np.all(amounts >= 0), name
