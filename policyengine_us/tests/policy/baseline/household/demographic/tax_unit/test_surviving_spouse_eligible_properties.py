"""Exhaustive property checks for surviving spouse filing status.

YAML cases check one household each. These tests build every combination
on the grid below as its own tax unit in one vectorized simulation and
check properties that must hold for all of them: eligibility never depends
on the dependent's income, never comes from a non-child dependent, and adds
to the previous rule only the units it rejected for the gross income test.

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
# Households without parent ids: an unmarked dependent, or one marked as a
# parent, grandparent or unrelated person. Households with parent ids: the
# dependent's id names the head, names an absent parent, or is unknown
# while the head's own id is set.
RELATIONSHIPS = [
    "unmarked",
    "parent",
    "grandparent",
    "unrelated",
    "linked_to_head",
    "linked_elsewhere",
    "unlinked_in_linked_household",
]
CHILD = {"unmarked", "linked_to_head"}

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
        head, spouse, dependent = (f"{role}_{i}" for role in ("h", "s", "d"))
        head_id = 3 * i + 1
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
                "person_id": {year: head_id + 1},
                "age": {year: 65},
                "is_tax_unit_head": {year: False},
                "is_tax_unit_spouse": {year: True},
            }
        marital_units[f"m_{i}"] = {"members": members[:]}
        relationship = unit["relationship"]
        if relationship is not None:
            members.append(dependent)
            parent_1_id = {
                "linked_to_head": head_id,
                "linked_elsewhere": ABSENT_ID + i,
            }.get(relationship, 0)
            people[dependent] = {
                "person_id": {year: head_id + 2},
                "parent_1_id": {year: parent_1_id},
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
            if relationship == "unlinked_in_linked_household":
                people[head]["parent_1_id"] = {year: ABSENT_ID + i}
            marital_units[f"dm_{i}"] = {"members": [dependent]}
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

    relationship = _field("relationship", "")
    return {
        "eligible": calc("surviving_spouse_eligible"),
        "hoh": calc("head_of_household_eligible"),
        "filing_status": sim.calculate("filing_status", PERIOD).decode_to_str(),
        "child_dependents": calc("tax_unit_child_dependents"),
        "surviving": _field("surviving", False),
        "married": _field("married", False),
        "has_dependent": relationship != "",
        "is_child": np.isin(relationship, list(CHILD)),
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
    with_dependent = sum(unit["relationship"] is not None for unit in UNITS)
    assert len(groups) * len(INCOMES) == with_dependent
    assert all(len(values) == 1 for values in groups.values())


def test_non_child_dependents_never_qualify(grid):
    not_child = grid["has_dependent"] & ~grid["is_child"]
    assert not_child.any()
    assert not grid["eligible"][not_child].any()


def test_eligibility_requires_unmarried_surviving_spouse_with_dependent(grid):
    eligible = grid["eligible"]
    assert eligible.any()
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
