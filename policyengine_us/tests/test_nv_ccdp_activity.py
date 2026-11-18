"""Invariants of Nevada's Purpose of Care activity test.

Manual MS 400 requires an activity of the applicant and every other required
adult. MS 420 counts paid work with no minimum hours. MS 470 covers a disabled
caretaker only when someone else can care for the child.

1. Without another pathway, the result follows the table in expected_activity
   for every pair of caretakers.
2. Earnings can only add eligibility for a lone caretaker, at any amount.
3. An adult in a tax unit that claims no eligible child changes nothing,
   whatever that adult does.
4. With parent ids, the linked parent's activity decides, whoever claims the
   child and whatever that claimant does.

YAML pins single households. These tests need Hypothesis to walk every pair of
caretakers against a reference written apart from the formula.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
MONTH = "2025-01"

CARETAKER = st.fixed_dictionaries(
    {
        "earnings": st.sampled_from([0, 1, 12_000]),
        "student": st.booleans(),
        "disabled": st.booleans(),
    }
)


def expected_activity(caretakers):
    """The manual's rule, written apart from the formula as a reference."""
    active = [c["earnings"] > 0 or c["student"] for c in caretakers]
    covered = [a or c["disabled"] for a, c in zip(active, caretakers)]
    return any(active) and all(covered)


def adult(caretaker, age=30):
    return {
        "age": {YEAR: age},
        "employment_income": {YEAR: caretaker["earnings"]},
        "is_full_time_college_student": {YEAR: caretaker["student"]},
        "is_disabled": {YEAR: caretaker["disabled"]},
    }


def eligible(people, tax_units):
    members = list(people)
    situation = {
        "people": people,
        "tax_units": tax_units,
        "spm_units": {"spm_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "households": {"household": {"members": members, "state_name": {YEAR: "NV"}}},
    }
    simulation = Simulation(situation=situation)
    return bool(simulation.calculate("nv_ccdp_activity_eligible", MONTH)[0])


def activity_eligible(caretakers, other_adult=None):
    people = {
        f"caretaker{index}": adult(caretaker)
        for index, caretaker in enumerate(caretakers)
    }
    people["child"] = {"age": {YEAR: 4}}
    tax_units = {"tax_unit": {"members": list(people)}}
    if other_adult is not None:
        people["other_adult"] = adult(other_adult, age=65)
        tax_units["other_tax_unit"] = {"members": ["other_adult"]}
    return eligible(people, tax_units)


@settings(max_examples=30, deadline=None)
@given(caretakers=st.lists(CARETAKER, min_size=1, max_size=2))
def test_activity_follows_the_manual(caretakers):
    assert activity_eligible(caretakers) == expected_activity(caretakers)


@settings(max_examples=15, deadline=None)
@given(
    caretakers=st.lists(CARETAKER, min_size=1, max_size=2),
    other_adult=CARETAKER,
)
def test_an_adult_who_claims_no_child_changes_nothing(caretakers, other_adult):
    assert activity_eligible(caretakers, other_adult=other_adult) == (
        expected_activity(caretakers)
    )


@settings(max_examples=15, deadline=None)
@given(earnings=st.integers(min_value=1, max_value=200_000))
def test_any_paid_work_is_enough_for_a_lone_parent(earnings):
    parent = {"earnings": earnings, "student": False, "disabled": False}
    assert activity_eligible([parent])


@settings(max_examples=15, deadline=None)
@given(parent=CARETAKER, claimant=CARETAKER)
def test_a_linked_parent_decides_whoever_claims_the_child(parent, claimant):
    people = {
        "parent": {**adult(parent), "person_id": {YEAR: 1}},
        "child": {
            "age": {YEAR: 4},
            "person_id": {YEAR: 2},
            "parent_1_id": {YEAR: 1},
        },
        "claimant": {**adult(claimant, age=65), "person_id": {YEAR: 3}},
    }
    tax_units = {
        "parent_tax_unit": {"members": ["parent"]},
        "claimant_tax_unit": {"members": ["claimant", "child"]},
    }
    assert eligible(people, tax_units) == expected_activity([parent])
