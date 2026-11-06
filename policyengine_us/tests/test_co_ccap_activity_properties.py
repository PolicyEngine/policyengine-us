"""Invariants of Colorado's child care activity requirement.

8 CCR 1403-1 section 3.111(B)(1) requires caretakers to take part in an eligible
activity, and (D) and (E) say which households qualify.

1. A caretaker works when earnings are positive and at least the federal minimum
   wage for the hours worked (3.111(G)(1)(b) and (G)(2)(d)). Without the exempt
   paths, a household qualifies when a caretaker is in an activity and every other
   caretaker is in an activity or incapacitated (3.111(D)(1)(c), 3.111(E)).
2. No family without the requirement receives a subsidy: co_ccap_eligible implies
   co_ccap_activity_eligible, and co_ccap_subsidy is zero without it.
3. Raising a caretaker's earnings never removes eligibility while hours stay the
   same.
4. An adult who files separately and claims no eligible child doesn't change the
   answer, whatever that adult earns.
5. The exempt paths each qualify a family with no activity (3.116(A), 3.119(D),
   3.121(B)(3)(a), and the activity input).

The YAML cases pin single families. These generate earnings, hours, weeks and
family makeups, which YAML can't express.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = "2026-01"
MINIMUM_WAGE = 7.25
WEEKS_IN_YEAR = 52

caretakers = st.fixed_dictionaries(
    {
        "wages": st.integers(min_value=0, max_value=60_000),
        "business": st.integers(min_value=-30_000, max_value=60_000),
        "hours": st.integers(min_value=0, max_value=70),
        "weeks": st.integers(min_value=0, max_value=52),
        "student": st.booleans(),
        "disabled": st.booleans(),
    }
)


def person_input(caretaker):
    return {
        "age": {YEAR: 30},
        "employment_income": {YEAR: caretaker["wages"]},
        "self_employment_income": {YEAR: caretaker["business"]},
        "weekly_hours_worked_before_lsr": {YEAR: caretaker["hours"]},
        "weeks_worked": {YEAR: caretaker["weeks"]},
        "is_full_time_college_student": {YEAR: caretaker["student"]},
        "is_disabled": {YEAR: caretaker["disabled"]},
    }


def simulate(caretakers, spm_unit=None, household=None, other_adult=None, child=None):
    names = [f"caretaker{index}" for index in range(len(caretakers))]
    people = {name: person_input(item) for name, item in zip(names, caretakers)}
    people["child"] = {"age": {YEAR: 3}, **(child or {})}
    family = names + ["child"]
    tax_units = {"claiming": {"members": family}}
    members = list(family)
    if other_adult is not None:
        people["other_adult"] = {"age": {YEAR: 60}, **other_adult}
        tax_units["other"] = {"members": ["other_adult"]}
        members.append("other_adult")
    situation = {
        "people": people,
        "tax_units": tax_units,
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_pre_subsidy_childcare_expenses": {YEAR: 12_000},
                **(spm_unit or {}),
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {name: {"members": [name]} for name in people},
        "households": {
            "household": {
                "members": members,
                "state_name": {YEAR: "CO"},
                **(household or {}),
            }
        },
    }
    return Simulation(situation=situation)


def activity_eligible(simulation):
    return bool(simulation.calculate("co_ccap_activity_eligible", MONTH)[0])


def in_activity(caretaker):
    earnings = max(caretaker["wages"], 0) + max(caretaker["business"], 0)
    weeks = caretaker["weeks"] or WEEKS_IN_YEAR
    floor = MINIMUM_WAGE * caretaker["hours"] * weeks
    return caretaker["student"] or (earnings > 0 and earnings >= floor)


def rule_says_eligible(caretakers):
    active = [in_activity(item) for item in caretakers]
    covered = [
        is_active or item["disabled"] for is_active, item in zip(active, caretakers)
    ]
    return any(active) and all(covered)


@settings(max_examples=25, deadline=None)
@given(family=st.lists(caretakers, min_size=1, max_size=2))
# A dollar below and exactly at the floor for 2,080 hours.
@example(
    family=[
        {
            "wages": 15_079,
            "business": 0,
            "hours": 40,
            "weeks": 52,
            "student": False,
            "disabled": False,
        }
    ]
)
@example(
    family=[
        {
            "wages": 15_080,
            "business": 0,
            "hours": 40,
            "weeks": 52,
            "student": False,
            "disabled": False,
        }
    ]
)
# An incapacitated caretaker alone, and beside a working caretaker.
@example(
    family=[
        {
            "wages": 0,
            "business": 0,
            "hours": 0,
            "weeks": 0,
            "student": False,
            "disabled": True,
        }
    ]
)
@example(
    family=[
        {
            "wages": 20_000,
            "business": 0,
            "hours": 0,
            "weeks": 0,
            "student": False,
            "disabled": False,
        },
        {
            "wages": 0,
            "business": 0,
            "hours": 0,
            "weeks": 0,
            "student": False,
            "disabled": True,
        },
    ]
)
def test_activity_requirement_follows_the_rule(family):
    simulation = simulate(family)
    assert activity_eligible(simulation) == rule_says_eligible(family)


@settings(max_examples=15, deadline=None)
@given(family=st.lists(caretakers, min_size=1, max_size=2))
def test_no_family_without_the_requirement_receives_a_subsidy(family):
    simulation = simulate(family)
    eligible = bool(simulation.calculate("co_ccap_eligible", MONTH)[0])
    subsidy = float(simulation.calculate("co_ccap_subsidy", MONTH)[0])
    if not activity_eligible(simulation):
        assert not eligible
        assert subsidy == 0
    if eligible:
        assert activity_eligible(simulation)
    assert subsidy >= 0


@settings(max_examples=15, deadline=None)
@given(
    family=st.lists(caretakers, min_size=1, max_size=2),
    raise_by=st.integers(min_value=1, max_value=40_000),
)
def test_more_earnings_never_remove_the_activity(family, raise_by):
    before = activity_eligible(simulate(family))
    raised = [{**family[0], "wages": family[0]["wages"] + raise_by}] + family[1:]
    after = activity_eligible(simulate(raised))
    assert after >= before


@settings(max_examples=15, deadline=None)
@given(
    family=st.lists(caretakers, min_size=1, max_size=2),
    other_earnings=st.integers(min_value=0, max_value=60_000),
)
def test_a_separate_filer_does_not_change_the_answer(family, other_earnings):
    alone = activity_eligible(simulate(family))
    beside = simulate(family, other_adult={"employment_income": {YEAR: other_earnings}})
    assert activity_eligible(beside) == alone


NO_ACTIVITY = {
    "wages": 0,
    "business": 0,
    "hours": 0,
    "weeks": 0,
    "student": False,
    "disabled": False,
}


def test_a_family_with_no_activity_fails_without_an_exempt_path():
    assert not activity_eligible(simulate([NO_ACTIVITY]))


@pytest.mark.parametrize(
    "path",
    [
        {"spm_unit": {"is_tanf_enrolled": {MONTH: True}}},
        {"spm_unit": {"meets_ccdf_activity_test": {YEAR: True}}},
        {"household": {"is_homeless": {YEAR: True}}},
        {"child": {"receives_or_needs_protective_services": {YEAR: True}}},
        {"child": {"is_in_foster_care": {MONTH: True}}},
    ],
)
def test_each_exempt_path_qualifies_a_family_with_no_activity(path):
    assert activity_eligible(simulate([NO_ACTIVITY], **path))
