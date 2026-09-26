"""Invariants for inferring the tax unit head and spouse.

``is_tax_unit_head`` picks the oldest adult and ``is_tax_unit_spouse`` the
next oldest, skipping anyone input as a tax unit dependent unless every adult
in the unit is one. These tests enumerate every tax unit of up to three people
drawn from a small grid of ages and dependent inputs, and compare the model
against reference implementations of that rule and of the rule before
dependent inputs were honoured.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
# Covers children, the age-18 adult boundary, and ties between adults.
AGES = (10, 18, 40, 70)
MAX_UNIT_SIZE = 3


def _all_units(flag_values):
    options = list(itertools.product(AGES, flag_values))
    units = []
    for size in range(1, MAX_UNIT_SIZE + 1):
        units.extend(itertools.product(options, repeat=size))
    return units


UNITS = _all_units((False, True))
UNFLAGGED_UNITS = _all_units((False,))


def _simulate(units, dependent_input: bool) -> Simulation:
    people = {}
    groups = {}
    for unit_index, members in enumerate(units):
        names = []
        for position, (age, flagged) in enumerate(members):
            name = f"unit_{unit_index}_person_{position}"
            person = {"age": {str(YEAR): age}}
            if dependent_input:
                person["is_tax_unit_dependent"] = {str(YEAR): flagged}
            people[name] = person
            names.append(name)
        groups[f"unit_{unit_index}"] = {"members": names}
    return Simulation(
        situation={
            "people": people,
            "tax_units": groups,
            "families": groups,
            "spm_units": groups,
            "households": groups,
        }
    )


def _reference_roles(members, honour_dependent_input: bool):
    """Positions of the head and spouse, ranking older first, then earlier."""
    adults = [i for i, (age, _) in enumerate(members) if age >= 18]
    candidates = adults
    if honour_dependent_input:
        non_dependents = [i for i in adults if not members[i][1]]
        if non_dependents:
            candidates = non_dependents
    ranked = sorted(candidates, key=lambda i: (-members[i][0], i))
    head = ranked[0] if ranked else None
    spouse = ranked[1] if len(ranked) > 1 else None
    return head, spouse


def _model_roles(sim, units):
    head = sim.calculate("is_tax_unit_head", YEAR)
    spouse = sim.calculate("is_tax_unit_spouse", YEAR)
    roles = []
    start = 0
    for members in units:
        stop = start + len(members)
        unit_head = np.flatnonzero(head[start:stop])
        unit_spouse = np.flatnonzero(spouse[start:stop])
        roles.append((unit_head.tolist(), unit_spouse.tolist()))
        start = stop
    return roles


def _as_lists(head, spouse):
    return (
        [] if head is None else [head],
        [] if spouse is None else [spouse],
    )


@pytest.fixture(scope="module")
def flagged_sim():
    return _simulate(UNITS, dependent_input=True)


def test_roles_follow_reference_rule_with_dependent_inputs(flagged_sim):
    model = _model_roles(flagged_sim, UNITS)
    mismatches = [
        (members, roles, _as_lists(*_reference_roles(members, True)))
        for members, roles in zip(UNITS, model)
        if roles != _as_lists(*_reference_roles(members, True))
    ]
    assert not mismatches, mismatches[:5]


def test_units_without_true_dependent_inputs_keep_previous_roles(flagged_sim):
    # Differential check: explicit false inputs match the previous rule.
    model = _model_roles(flagged_sim, UNITS)
    for members, roles in zip(UNITS, model):
        if not any(flagged for _, flagged in members):
            assert roles == _as_lists(*_reference_roles(members, False)), members


def test_roles_without_dependent_inputs_keep_previous_rule():
    sim = _simulate(UNFLAGGED_UNITS, dependent_input=False)
    model = _model_roles(sim, UNFLAGGED_UNITS)
    for members, roles in zip(UNFLAGGED_UNITS, model):
        assert roles == _as_lists(*_reference_roles(members, False)), members


def test_role_structure(flagged_sim):
    model = _model_roles(flagged_sim, UNITS)
    for members, (head, spouse) in zip(UNITS, model):
        has_adult = any(age >= 18 for age, _ in members)
        assert len(head) == (1 if has_adult else 0), members
        assert len(spouse) <= 1, members
        assert not set(head) & set(spouse), members
        for position in head + spouse:
            assert members[position][0] >= 18, members
        has_non_dependent_adult = any(
            age >= 18 and not flagged for age, flagged in members
        )
        if has_non_dependent_adult:
            for position in head + spouse:
                assert not members[position][1], members


def test_dependent_inputs_are_kept(flagged_sim):
    flags = [flagged for members in UNITS for _, flagged in members]
    dependent = flagged_sim.calculate("is_tax_unit_dependent", YEAR)
    assert dependent.tolist() == flags


def test_computed_dependents_do_not_change_roles():
    # Without inputs, is_tax_unit_dependent comes from head and spouse. Asking
    # for it first must not create a cycle or change which roles come out.
    units = UNFLAGGED_UNITS
    dependent_first = _simulate(units, dependent_input=False)
    dependent = dependent_first.calculate("is_tax_unit_dependent", YEAR)
    head = dependent_first.calculate("is_tax_unit_head", YEAR)
    spouse = dependent_first.calculate("is_tax_unit_spouse", YEAR)
    np.testing.assert_array_equal(dependent, ~head & ~spouse)
    # Recomputing head and spouse after the dependent flags are cached.
    for variable in ("is_tax_unit_head", "is_tax_unit_spouse"):
        dependent_first.get_holder(variable).delete_arrays()
    assert _model_roles(dependent_first, units) == _model_roles(
        _simulate(units, dependent_input=False), units
    )


def test_dependent_input_in_a_branch_is_honoured():
    members = ((40, False), (70, True))
    sim = _simulate([members], dependent_input=False)
    branch = sim.get_branch("dependent_parent")
    branch.set_input("is_tax_unit_dependent", YEAR, np.array([False, True]))
    assert branch.calculate("is_tax_unit_head", YEAR).tolist() == [True, False]
    assert sim.calculate("is_tax_unit_head", YEAR).tolist() == [False, True]
