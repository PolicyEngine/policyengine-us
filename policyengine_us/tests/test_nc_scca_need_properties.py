"""Invariants of North Carolina's need for child care.

10A NCAC 10 .0905 and Chapter 5 of the Subsidized Child Care Assistance Program
Policy Manual say which families have a need.

1. Without the other paths, a family has a need when each parent or responsible
   adult works, studies, or can't work and provide care (.0905(a), (b) and (f);
   Chapter 5 III.A). Any positive earnings count.
2. No family without a need receives a subsidy: nc_scca_entry_eligible implies
   nc_scca_need_eligible, and nc_scca is zero without it.
3. Giving an adult earnings never removes the need.
4. An adult who files separately and claims no eligible child doesn't change the
   answer, whatever that adult earns.
5. The other paths each give a need to a family with no activity (Chapter 5 III.B.5,
   III.D and III.E, and the activity input).

The YAML cases pin single families. These generate earnings and family makeups,
which YAML can't express. Tests of the need itself fix the child as eligible, so
an income above the program's limit can't empty the test.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = "2026-01"

adults = st.fixed_dictionaries(
    {
        "wages": st.integers(min_value=0, max_value=60_000),
        "business": st.integers(min_value=-30_000, max_value=60_000),
        "student": st.booleans(),
        "disabled": st.booleans(),
    }
)

IDLE = {"wages": 0, "business": 0, "student": False, "disabled": False}
WORKING = {"wages": 20_000, "business": 0, "student": False, "disabled": False}
ELIGIBLE_CHILD = {"nc_scca_child_eligible": {MONTH: True}}


def person_input(adult):
    return {
        "age": {YEAR: 30},
        "employment_income": {YEAR: adult["wages"]},
        "self_employment_income": {YEAR: adult["business"]},
        "is_full_time_college_student": {YEAR: adult["student"]},
        "is_disabled": {YEAR: adult["disabled"]},
    }


def simulate(adults, spm_unit=None, other_adult=None, child=ELIGIBLE_CHILD):
    names = [f"adult{index}" for index in range(len(adults))]
    people = {name: person_input(item) for name, item in zip(names, adults)}
    people["child"] = {"age": {YEAR: 3}, **child}
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
                "state_name": {YEAR: "NC"},
                "county_str": {YEAR: "WAKE_COUNTY_NC"},
            }
        },
    }
    return Simulation(situation=situation)


def has_need(simulation):
    return bool(simulation.calculate("nc_scca_need_eligible", MONTH)[0])


def adult_has_need(adult):
    earns = adult["wages"] > 0 or adult["business"] > 0
    return earns or adult["student"] or adult["disabled"]


@settings(max_examples=25, deadline=None)
@given(family=st.lists(adults, min_size=1, max_size=2))
# One adult with no activity, alone and beside a working adult; a single adult who
# can't work or provide care; and a business loss beside wages.
@example(family=[IDLE])
@example(family=[WORKING, IDLE])
@example(family=[{**IDLE, "disabled": True}])
@example(family=[{**WORKING, "business": -30_000}])
def test_need_follows_the_rule(family):
    simulation = simulate(family)
    assert has_need(simulation) == all(adult_has_need(item) for item in family)


@settings(max_examples=15, deadline=None)
@given(family=st.lists(adults, min_size=1, max_size=2))
def test_no_family_without_a_need_receives_a_subsidy(family):
    # This test runs the child's own age and income tests.
    simulation = simulate(family, child={})
    entry_eligible = bool(simulation.calculate("nc_scca_entry_eligible", MONTH)[0])
    subsidy = float(simulation.calculate("nc_scca", MONTH)[0])
    if entry_eligible:
        assert has_need(simulation)
    if not entry_eligible:
        assert subsidy == 0
    if not has_need(simulation):
        assert not entry_eligible
    assert subsidy >= 0


@settings(max_examples=15, deadline=None)
@given(
    family=st.lists(adults, min_size=1, max_size=2),
    raise_by=st.integers(min_value=1, max_value=40_000),
)
def test_earnings_never_remove_the_need(family, raise_by):
    before = has_need(simulate(family))
    raised = [{**family[0], "wages": family[0]["wages"] + raise_by}] + family[1:]
    assert has_need(simulate(raised)) >= before


@settings(max_examples=15, deadline=None)
@given(
    family=st.lists(adults, min_size=1, max_size=2),
    other_earnings=st.integers(min_value=0, max_value=60_000),
)
def test_a_separate_filer_does_not_change_the_answer(family, other_earnings):
    alone = has_need(simulate(family))
    beside = simulate(family, other_adult={"employment_income": {YEAR: other_earnings}})
    assert has_need(beside) == alone


def test_a_family_with_no_activity_has_no_need_without_another_path():
    assert not has_need(simulate([IDLE]))


@pytest.mark.parametrize(
    "path",
    [
        {"spm_unit": {"is_tanf_enrolled": {MONTH: True}}},
        {"spm_unit": {"meets_ccdf_activity_test": {YEAR: True}}},
        {"child": {**ELIGIBLE_CHILD, "is_disabled": {YEAR: True}}},
        {
            "child": {
                **ELIGIBLE_CHILD,
                "receives_or_needs_protective_services": {YEAR: True},
            }
        },
    ],
)
def test_each_other_path_gives_a_family_with_no_activity_a_need(path):
    assert has_need(simulate([IDLE], **path))
