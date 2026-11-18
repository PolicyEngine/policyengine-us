"""Invariants of the Wisconsin Works payment by unsubsidized hours.

Wis. Stat. 49.148(1)(b)1m and W-2 Manual 7.4.1.5 set the Community Service Job
payment by a participant's hours of unsubsidized work.

1. The payment matches the manual's table at every weekly hour.
2. The payment never rises with hours, and it stays between $0 and the CSJ amount.
3. Payments for an infant or an at-risk pregnancy ignore hours.
4. Swapping the two parents' hours changes nothing, and the parent with fewer
   hours sets the payment.
5. An adult in a tax unit that claims no child changes nothing, whether or not
   the data count that adult as a parent.

YAML pins single households. These tests need every hour and Hypothesis to walk
the table against a reference written apart from the formula.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEAR = 2025
MONTH = "2025-01"
CSJ = 653
CMC = 673
HOURS = st.integers(min_value=0, max_value=60)


def manual_payment(hours):
    """The table in W-2 Manual 7.4.1.5, written out as an independent reference."""
    if hours < 10:
        return 653
    if hours < 15:
        return 435
    if hours < 20:
        return 327
    if hours < 30:
        return 218
    return 0


def payment(parent_hours, child_age=5, other_adult=None):
    people = {
        f"parent{index}": {
            "age": {YEAR: 30},
            "weekly_hours_worked_before_lsr": {YEAR: hours},
            "own_children_in_household": {YEAR: 1},
        }
        for index, hours in enumerate(parent_hours)
    }
    people["child"] = {"age": {YEAR: child_age}}
    tax_units = {"tax_unit": {"members": list(people)}}
    if other_adult is not None:
        hours, children = other_adult
        people["other_adult"] = {
            "age": {YEAR: 60},
            "weekly_hours_worked_before_lsr": {YEAR: hours},
            "own_children_in_household": {YEAR: children},
        }
        tax_units["other_tax_unit"] = {"members": ["other_adult"]}
    members = list(people)
    situation = {
        "people": people,
        "tax_units": tax_units,
        "spm_units": {
            "spm_unit": {"members": members, "wi_works_eligible": {MONTH: True}}
        },
        "families": {"family": {"members": members}},
        "households": {"household": {"members": members, "state_name": {YEAR: "WI"}}},
    }
    return float(Simulation(situation=situation).calculate("wi_works", MONTH)[0])


@pytest.mark.parametrize("hours", range(0, 41))
def test_payment_matches_the_manual_table(hours):
    assert payment([hours]) == manual_payment(hours)


@settings(max_examples=25, deadline=None)
@given(lower=HOURS, extra=HOURS)
def test_payment_never_rises_with_hours(lower, extra):
    low_hours = payment([lower])
    high_hours = payment([lower + extra])
    assert 0 <= high_hours <= low_hours <= CSJ


@settings(max_examples=10, deadline=None)
@given(hours=HOURS)
def test_infant_payment_ignores_hours(hours):
    assert payment([hours], child_age=0) == CMC


@settings(max_examples=25, deadline=None)
@given(first=HOURS, second=HOURS)
def test_the_parent_with_fewer_hours_sets_the_payment(first, second):
    assert payment([first, second]) == payment([second, first])
    assert payment([first, second]) == manual_payment(min(first, second))


@settings(max_examples=15, deadline=None)
@given(hours=HOURS, other_hours=HOURS, other_children=st.integers(0, 2))
def test_an_adult_who_claims_no_child_changes_nothing(
    hours, other_hours, other_children
):
    other_adult = (other_hours, other_children)
    assert payment([hours], other_adult=other_adult) == manual_payment(hours)


def test_the_share_starts_with_act_9():
    parameters = CountryTaxBenefitSystem().parameters
    share = "gov.states.wi.dcf.works.placement.csj_share"
    before = parameters.get_child(share)("1999-10-28")
    after = parameters.get_child(share)("1999-10-29")
    assert [before.calc(hours) for hours in (0, 10, 15, 20, 30)] == [1] * 5
    assert after.calc(30) == 0
