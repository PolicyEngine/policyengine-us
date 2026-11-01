"""Invariants of Nevada's Purpose of Care activity test.

Manual MS 400 requires an activity of the applicant and every other required
adult. MS 420 counts paid work with no minimum hours. MS 470 covers a disabled
caretaker only when someone else can care for the child.

1. Without the input or another pathway, the result follows the table in
   expected_activity for every pair of caretakers.
2. The input can only add eligibility: setting it never removes it.
3. Earnings can only add eligibility for a lone caretaker, at any amount.
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


def activity_eligible(caretakers, meets_test=False):
    people = {
        f"caretaker{index}": {
            "age": {YEAR: 30},
            "employment_income": {YEAR: caretaker["earnings"]},
            "is_full_time_college_student": {YEAR: caretaker["student"]},
            "is_disabled": {YEAR: caretaker["disabled"]},
        }
        for index, caretaker in enumerate(caretakers)
    }
    people["child"] = {"age": {YEAR: 4}}
    members = list(people)
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "meets_ccdf_activity_test": {YEAR: meets_test},
            }
        },
        "families": {"family": {"members": members}},
        "households": {"household": {"members": members, "state_name": {YEAR: "NV"}}},
    }
    simulation = Simulation(situation=situation)
    return bool(simulation.calculate("nv_ccdp_activity_eligible", MONTH)[0])


@settings(max_examples=30, deadline=None)
@given(caretakers=st.lists(CARETAKER, min_size=1, max_size=2))
def test_activity_follows_the_manual(caretakers):
    assert activity_eligible(caretakers) == expected_activity(caretakers)


@settings(max_examples=15, deadline=None)
@given(caretakers=st.lists(CARETAKER, min_size=1, max_size=2))
def test_the_input_only_adds_eligibility(caretakers):
    assert activity_eligible(caretakers, meets_test=True)


@settings(max_examples=15, deadline=None)
@given(earnings=st.integers(min_value=1, max_value=200_000))
def test_any_paid_work_is_enough_for_a_lone_parent(earnings):
    parent = {"earnings": earnings, "student": False, "disabled": False}
    assert activity_eligible([parent])
