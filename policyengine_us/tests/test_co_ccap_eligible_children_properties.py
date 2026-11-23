"""Colorado's Child Care Assistance Program pays only for eligible children.

8 CCR 1403-1 3.132(D) and (E) pay for the care of children under 13, and of
children under 19 who can't care for themselves or who are under court
supervision (3.103(UU) and 3.111(F) define the eligible child the same way).

1. A member outside those limits, such as a 15-year-old without additional
   care needs or a 19-year-old, adds nothing to the payment, whatever that
   member's charges, the eligible child's charges or the parent fee.
2. The payment equals the eligible children's child care and after-school
   charges, each child's capped at the county rate for that child's care
   (3.125(FFF) and 3.130), less the parent fee, and never falls below zero.

The tests set eligibility and the parent fee as inputs, so they exercise the
payment formula alone.
"""

from decimal import ROUND_HALF_UP, Decimal

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = f"{YEAR}-01"
TOLERANCE = 0.01
AGE_LIMIT = 13
ADDITIONAL_NEEDS_AGE_LIMIT = 19
MONTHS_IN_YEAR = 12
# These households report no county, provider, rating or schedule, so the
# county rate reads an Adams County center at Tier 1 & Tier 2, full time, five
# days a week. CDEC's table effective October 1, 2025 sets Adams County's
# daily rates by age band, in months.
ADAMS_CENTER_DAILY_RATES = ((18, 76.71), (36, 62.26), (72, 44.24))
ADAMS_CENTER_SCHOOL_AGE_DAILY_RATE = 37.33
DAYS_PER_MONTH = 5 * 52 / 12
# A child in school (PolicyEngine puts ages 5 to 17 there) aged 6 or older
# whose only charge comes after school takes the part-time unit, 55% of the
# daily rate rounded half up to the cent (3.130(C)).
FIRST_GRADE_AGE = 6
LAST_SCHOOL_AGE = 17
PART_TIME_UNIT = Decimal("0.55")


def colorado(children, monthly_fee):
    """January payment for an SPM unit of one parent and these children."""
    members = ["parent", *children]
    people = {"parent": {"age": {YEAR: 30}}}
    for name, child in children.items():
        people[name] = {
            "age": {YEAR: child["age"]},
            "is_tax_unit_dependent": {YEAR: True},
            "is_disabled": {YEAR: child["disabled"]},
            "is_under_court_supervision": {YEAR: child["court"]},
            "pre_subsidy_childcare_expenses": {YEAR: child["care"] * 12},
            "after_school_expenses": {YEAR: child["after_school"] * 12},
        }
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "co_ccap_eligible": {MONTH: True},
                "co_ccap_parent_fee": {MONTH: monthly_fee},
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {YEAR: "CO"}}},
    }
    simulation = Simulation(situation=situation)
    return float(simulation.calculate("co_ccap_subsidy", MONTH)[0])


def eligible(child):
    """3.132(D) and (E): under 13, or under 19 with additional care needs."""
    return child["age"] < AGE_LIMIT or (
        (child["disabled"] or child["court"])
        and child["age"] < ADDITIONAL_NEEDS_AGE_LIMIT
    )


def full_time_daily_rate(child):
    age_months = child["age"] * MONTHS_IN_YEAR
    for limit, daily in ADAMS_CENTER_DAILY_RATES:
        if age_months < limit:
            return daily
    return ADAMS_CENTER_SCHOOL_AGE_DAILY_RATE


def county_rate(child):
    """3.130: the most Adams County pays for the child's care in a month."""
    daily = full_time_daily_rate(child)
    after_school_only = (
        FIRST_GRADE_AGE <= child["age"] <= LAST_SCHOOL_AGE
        and child["care"] == 0
        and child["after_school"] > 0
    )
    if after_school_only:
        part_time = Decimal(str(daily)) * PART_TIME_UNIT
        daily = float(part_time.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return daily * DAYS_PER_MONTH


charges = dict(
    care=st.integers(min_value=0, max_value=2_000),
    after_school=st.integers(min_value=0, max_value=800),
)
needs = st.sampled_from([(True, False), (False, True), (True, True)])
young_children = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=0, max_value=AGE_LIMIT - 1),
        disabled=st.booleans(),
        court=st.booleans(),
        **charges,
    )
)
children_with_needs = st.builds(
    lambda age, need, care, after_school: dict(
        age=age,
        disabled=need[0],
        court=need[1],
        care=care,
        after_school=after_school,
    ),
    age=st.integers(min_value=AGE_LIMIT, max_value=ADDITIONAL_NEEDS_AGE_LIMIT - 1),
    need=needs,
    **charges,
)
eligible_children = st.one_of(young_children, children_with_needs)
teenagers = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=AGE_LIMIT, max_value=ADDITIONAL_NEEDS_AGE_LIMIT - 1),
        disabled=st.just(False),
        court=st.just(False),
        **charges,
    )
)
older_members = st.fixed_dictionaries(
    dict(
        age=st.integers(
            min_value=ADDITIONAL_NEEDS_AGE_LIMIT,
            max_value=ADDITIONAL_NEEDS_AGE_LIMIT + 3,
        ),
        disabled=st.booleans(),
        court=st.booleans(),
        **charges,
    )
)
ineligible_members = st.one_of(teenagers, older_members)


@settings(max_examples=15, deadline=None)
# A 3-year-old and a 15-year-old with $1,000 each and a $200 fee.
@example(
    child=dict(age=3, disabled=False, court=False, care=1_000, after_school=0),
    other=dict(age=15, disabled=False, court=False, care=1_000, after_school=0),
    fee=200,
)
# The age boundaries: 12 and 13, and 18 and 19 with a disability.
@example(
    child=dict(age=12, disabled=False, court=False, care=0, after_school=500),
    other=dict(age=13, disabled=False, court=False, care=0, after_school=500),
    fee=0,
)
@example(
    child=dict(age=18, disabled=True, court=False, care=900, after_school=0),
    other=dict(age=19, disabled=True, court=True, care=900, after_school=300),
    fee=50,
)
@given(child=eligible_children, other=ineligible_members, fee=st.integers(0, 500))
def test_a_member_outside_the_age_limits_adds_nothing(child, other, fee):
    alone = colorado({"child": child}, fee)
    with_other = colorado({"child": child, "other": other}, fee)
    assert with_other == pytest.approx(alone, abs=TOLERANCE)


@settings(max_examples=20, deadline=None)
@example(
    children=[
        dict(age=3, disabled=False, court=False, care=1_000, after_school=0),
        dict(age=15, disabled=True, court=False, care=1_000, after_school=0),
        dict(age=15, disabled=False, court=False, care=1_000, after_school=0),
    ],
    fee=0,
)
# A fee above the eligible child's charges leaves nothing to pay.
@example(
    children=[
        dict(age=3, disabled=False, court=False, care=100, after_school=0),
        dict(age=15, disabled=False, court=False, care=1_000, after_school=0),
    ],
    fee=200,
)
# A 12-year-old whose only care comes after school takes the part-time unit
# ($20.53 a day), and a sibling with child care charges takes full time.
@example(
    children=[
        dict(age=12, disabled=False, court=False, care=0, after_school=800),
        dict(age=12, disabled=False, court=False, care=100, after_school=800),
    ],
    fee=0,
)
@given(
    children=st.lists(
        st.one_of(eligible_children, ineligible_members), min_size=1, max_size=3
    ),
    fee=st.integers(min_value=0, max_value=500),
)
def test_the_payment_equals_the_eligible_childrens_capped_charges_less_the_fee(
    children, fee
):
    named = {f"child_{i}": child for i, child in enumerate(children)}
    paid = colorado(named, fee)
    eligible_charges = sum(
        min(child["care"] + child["after_school"], county_rate(child))
        for child in children
        if eligible(child)
    )
    assert paid >= -TOLERANCE
    assert paid == pytest.approx(max(eligible_charges - fee, 0), abs=TOLERANCE)
