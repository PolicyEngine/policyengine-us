"""Exhaustive property checks for surviving spouse filing status.

The YAML cases check named households. These tests check properties that
must hold for every combination on the grid below, which YAML cannot state:
eligibility never changes with the dependent's income (units grouped by
everything but income), matches an independent reference rule written from
the grid's relationship labels, and differs from the previous rule (read from
tax_unit_child_dependents) only for children who fail the gross income test.
Every combination is its own tax unit in one vectorized simulation built on
the shared model.

IRC 2(a)(1)(B) requires a dependent son, stepson, daughter or stepdaughter,
with dependency determined without regard to IRC 152(b)(1), (b)(2) and
(d)(1)(B), so the qualifying relative gross income test does not apply.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

PERIOD = 2025
EXEMPTION_AMOUNT = system.parameters(PERIOD).gov.irs.income.exemption.amount

SURVIVING_SPOUSE = [True, False]
MARRIED = [False, True]
# Under 19 (qualifying child by age), an adult child, an elderly relative.
AGES = [10, 29, 88]
INCOMES = [0, 3_000, EXEMPTION_AMOUNT - 1, EXEMPTION_AMOUNT, 6_238, 50_000]
DISABLED = [False, True]
# How the dependent's relationship to the head is described. A parent id of
# 0 is unknown.
RELATIONSHIPS = {
    # No parent ids and no relationship flags.
    "unmarked": True,
    # Relationship flags without parent ids.
    "parent": False,
    "grandparent": False,
    "unrelated": False,
    # The dependent's first id names the head.
    "names_head": True,
    # The dependent's first id names an absent parent; the second is unknown.
    "names_absent_parent_only": True,
    # The dependent's ids name two absent parents.
    "names_two_absent_parents": False,
    # The dependent's first id names another (unrelated) tax unit member.
    "names_other_member": False,
    # The head's own id names an absent parent; the dependent has no ids.
    "head_has_ids": True,
    # The head's own id names the dependent as the head's parent.
    "named_as_head_parent": False,
}

UNITS = [
    dict(
        surviving=surviving,
        married=married,
        age=age,
        income=income,
        disabled=disabled,
        relationship=relationship,
    )
    for surviving, married, age, income, disabled, relationship in itertools.product(
        SURVIVING_SPOUSE, MARRIED, AGES, INCOMES, DISABLED, RELATIONSHIPS
    )
] + [
    dict(surviving=surviving, married=married, relationship=None)
    for surviving in SURVIVING_SPOUSE
    for married in MARRIED
]
# Ids that name no one in the simulation.
ABSENT_ID = 10_000_000


def _situation():
    year = str(PERIOD)
    people, tax_units, marital_units = {}, {}, {}
    for i, unit in enumerate(UNITS):
        head, spouse, dependent, other = (f"{r}_{i}" for r in ("h", "s", "d", "o"))
        head_id, spouse_id, dependent_id, other_id = (4 * i + k for k in (1, 2, 3, 4))
        members = [head]
        people[head] = {
            "person_id": {year: head_id},
            "age": {year: 67},
            "is_tax_unit_head": {year: True},
            "is_tax_unit_spouse": {year: False},
            "is_surviving_spouse": {year: unit["surviving"]},
        }
        if unit["married"]:
            members.append(spouse)
            people[spouse] = {
                "person_id": {year: spouse_id},
                "age": {year: 65},
                "is_tax_unit_head": {year: False},
                "is_tax_unit_spouse": {year: True},
            }
        marital_units[f"m_{i}"] = {"members": members[:]}
        relationship = unit["relationship"]
        if relationship is not None:
            members.append(dependent)
            parent_ids = {
                "names_head": (head_id, 0),
                "names_absent_parent_only": (ABSENT_ID + 2 * i, 0),
                "names_two_absent_parents": (ABSENT_ID + 2 * i, ABSENT_ID + 2 * i + 1),
                "names_other_member": (other_id, 0),
            }.get(relationship, (0, 0))
            people[dependent] = {
                "person_id": {year: dependent_id},
                "parent_1_id": {year: parent_ids[0]},
                "parent_2_id": {year: parent_ids[1]},
                "age": {year: unit["age"]},
                "is_tax_unit_head": {year: False},
                "is_tax_unit_spouse": {year: False},
                "is_tax_unit_dependent": {year: True},
                "employment_income": {year: unit["income"]},
                "is_permanently_and_totally_disabled": {year: unit["disabled"]},
                "is_parent_of_filer_or_spouse": {year: relationship == "parent"},
                "is_grandparent_of_filer_or_spouse": {
                    year: relationship == "grandparent"
                },
                "is_related_to_head_or_spouse": {year: relationship != "unrelated"},
            }
            marital_units[f"dm_{i}"] = {"members": [dependent]}
            if relationship == "head_has_ids":
                people[head]["parent_1_id"] = {year: ABSENT_ID + 2 * i}
            if relationship == "named_as_head_parent":
                people[head]["parent_1_id"] = {year: dependent_id}
            if relationship == "names_other_member":
                # The dependent's parent, also a dependent of the head but
                # marked unrelated, so never the head's child.
                members.append(other)
                people[other] = {
                    "person_id": {year: other_id},
                    "age": {year: 40},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: False},
                    "is_tax_unit_dependent": {year: True},
                    "is_related_to_head_or_spouse": {year: False},
                }
                marital_units[f"om_{i}"] = {"members": [other]}
        tax_units[f"t_{i}"] = {"members": members}

    def groups():
        return {
            name: {"members": unit["members"][:]} for name, unit in tax_units.items()
        }

    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": groups(),
        "families": groups(),
        "households": groups(),
    }


def _field(name, default):
    return np.array([unit.get(name, default) for unit in UNITS])


@pytest.fixture(scope="module")
def grid():
    sim = Simulation(situation=_situation())

    def calc(variable):
        return np.asarray(sim.calculate(variable, PERIOD))

    return {
        "eligible": calc("surviving_spouse_eligible"),
        "hoh": calc("head_of_household_eligible"),
        "filing_status": sim.calculate("filing_status", PERIOD).decode_to_str(),
        "child_dependents": calc("tax_unit_child_dependents"),
        "surviving": _field("surviving", False),
        "married": _field("married", False),
        "has_dependent": np.array([u["relationship"] is not None for u in UNITS]),
        "is_child": np.array(
            [RELATIONSHIPS.get(u["relationship"], False) for u in UNITS]
        ),
        "age": _field("age", -1),
        "income": _field("income", -1),
        "disabled": _field("disabled", False),
    }


def test_matches_reference_rule(grid):
    # A surviving spouse head, not remarried, with a dependent child.
    expected = grid["surviving"] & ~grid["married"] & grid["is_child"]
    assert len(grid["eligible"]) == len(UNITS)
    np.testing.assert_array_equal(grid["eligible"], expected)


def test_dependent_income_never_changes_eligibility(grid):
    groups = {}
    for i, unit in enumerate(UNITS):
        if unit["relationship"] is not None:
            key = tuple(value for name, value in unit.items() if name != "income")
            groups.setdefault(key, set()).add(bool(grid["eligible"][i]))
    assert len(groups) * len(INCOMES) == grid["has_dependent"].sum()
    assert all(len(values) == 1 for values in groups.values())


def test_non_child_dependents_never_qualify(grid):
    not_child = grid["has_dependent"] & ~grid["is_child"]
    assert not_child.any()
    assert not grid["eligible"][not_child].any()


def test_eligibility_requires_unmarried_surviving_spouse_with_dependent(grid):
    eligible = grid["eligible"]
    assert eligible.any()
    assert (~grid["has_dependent"]).sum() == len(SURVIVING_SPOUSE) * len(MARRIED)
    assert grid["surviving"][eligible].all()
    assert not grid["married"][eligible].any()
    assert grid["has_dependent"][eligible].all()


def test_filing_status_follows_eligibility(grid):
    eligible = grid["eligible"]
    np.testing.assert_array_equal(grid["filing_status"] == "SURVIVING_SPOUSE", eligible)
    assert not (eligible & grid["hoh"]).any()


def test_only_change_for_children_is_dropping_income_test(grid):
    # Differential against the previous rule, which counted child dependents
    # under is_child_dependent and so applied the gross income test.
    previous = grid["surviving"] & ~grid["married"] & (grid["child_dependents"] > 0)
    is_child = grid["is_child"]
    # Every child unit the previous rule accepted stays eligible.
    assert grid["eligible"][previous & is_child].all()
    # Units added are adult, non-disabled children whose income fails the
    # qualifying relative gross income test.
    added = grid["eligible"] & ~previous
    assert added.any()
    assert (grid["age"][added] >= 19).all()
    assert not grid["disabled"][added].any()
    assert (grid["income"][added] >= EXEMPTION_AMOUNT).all()
