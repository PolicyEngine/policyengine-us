"""Colorado's Child Care Assistance Program charges each household one parent fee.

8 CCR 1403-1 section 3.124 (ruleVersionId 12658, PDF pages 79-85) builds the
fee from gross countable income and household size: 1% of income plus 14% of
income above the federal poverty guideline ((P)(1) and (P)(2)), $15 for each
child in care after the first when income exceeds the guideline ((P)(3)), in
whole dollars ((A)), at 55% when every child in care receives part-time care
((U) and (W)), and 20% lower at a provider in the top three quality levels
((H)). The Department's parent fee tool drops the cents after each step.

Invariants, for every household:

1. The fee never falls below zero and always comes to whole dollars.
2. Until October 2028, with income and household size fixed, each child in
   care after the first adds $15 to the fee when income exceeds the guideline
   and nothing when it does not. The number of children in care changes the
   fee in no other way.
3. When every child in care receives part-time care, the fee falls to 55% of
   the full-time fee with the cents dropped. When any child in care receives
   full-time care, the household pays the full-time fee.
4. A provider in the top three quality levels, for any child in care, cuts the
   fee by 20% with the cents dropped. A lower rating, or a rating for a child
   outside care, changes nothing.

A differential test checks the model against `reference_fee`, an independent
implementation of the rule and the Department's tool in exact decimal
arithmetic, with the guidelines that section 3.111(H)(2) and (H)(3) list.
"""

from decimal import ROUND_FLOOR, Decimal

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
# Each child in care carries this monthly charge, so the child counts as in
# care whatever the schedule says.
MONTHLY_CHARGE = 400
# Section 3.111(H)(2) lists the guideline through September 2026, and section
# 3.111(H)(3) the one from October 2026: annual dollars for the first person
# and for each additional person.
GUIDELINES = {
    "2026-01": (Decimal(15_650), Decimal(5_500)),
    "2026-10": (Decimal(15_960), Decimal(5_680)),
}
# Without a schedule, the model reads care on each weekday.
ASSUMED_DAYS_PER_MONTH = Decimal(5 * 52) / 12


def floor(amount):
    return amount.to_integral_value(rounding=ROUND_FLOOR)


def daily_units(hours):
    """Full-time-equivalent units for a day of care (3.103(ZZ) and 3.130(C))."""
    if hours == 0:
        # The model reads unknown hours as a full-time day.
        return Decimal(1)
    if hours <= 5:
        return Decimal("0.55")
    if hours <= 12:
        return Decimal(1)
    if hours <= 17:
        return Decimal("1.55")
    return Decimal(2)


def part_time(child):
    """Fewer than 13 units a month (3.124(U)), or up to 5 hours a day for a
    child in grades 1 to 12 (3.124(W)). PolicyEngine has no grade input, so a
    child in school (ages 5 to 17) aged 6 or older counts as in grade 1 or
    above, as in the model. Days of care come from the larger of days a week
    x 52 / 12 and attending days a month, as in the model."""
    hours = Decimal(str(child["hours"]))
    scheduled_days = Decimal(child["week"] * 52) / 12
    days = max(scheduled_days, Decimal(child["days"])) or ASSUMED_DAYS_PER_MONTH
    in_grade_one_or_above = 6 <= child["age"] <= 17
    return daily_units(hours) * days < 13 or (in_grade_one_or_above and 0 < hours <= 5)


def guideline(month, children):
    """The annual guideline for a parent and these children."""
    first, additional = GUIDELINES[month]
    return first + additional * len(children)


def reference_fee(month, annual_income, children):
    """Section 3.124 and the Department's tool, step by step."""
    in_care = [child for child in children if child["in_care"]]
    if not in_care:
        return Decimal(0)
    income = max(Decimal(annual_income), Decimal(0))
    limit = guideline(month, children)
    base = (income * Decimal("0.01") + max(income - limit, 0) * Decimal("0.14")) / 12
    add_on = 15 * (len(in_care) - 1) if income > limit else 0
    fee = floor(base + add_on)
    if all(part_time(child) for child in in_care):
        fee = floor(fee * Decimal("0.55"))
    if max(child["rating"] for child in in_care) >= 3:
        fee = floor(fee * Decimal("0.8"))
    return fee


def fees(month, households):
    """The model's fee for each household, from one simulation.

    Each household holds one parent and the given children. A child in care
    has the given schedule and a monthly charge; a child outside care has
    neither."""
    year = int(month[:4])
    groups = ("tax_units", "spm_units", "families", "marital_units", "households")
    situation = {"people": {}, **{group: {} for group in groups}}
    for i, household in enumerate(households):
        parent = f"parent_{i}"
        members = [parent]
        situation["people"][parent] = {
            "age": {year: 35},
            "employment_income": {year: household["income"]},
            "self_employment_income": {year: household.get("loss", 0)},
        }
        for j, child in enumerate(household["children"]):
            name = f"child_{i}_{j}"
            person = {
                "age": {year: child["age"]},
                "is_tax_unit_dependent": {year: True},
                "co_quality_rating_of_child_care_facility": {year: child["rating"]},
            }
            if child["in_care"]:
                person["childcare_hours_per_day"] = {year: child["hours"]}
                person["childcare_attending_days_per_month"] = {year: child["days"]}
                person["childcare_days_per_week"] = {year: child["week"]}
                person["pre_subsidy_childcare_expenses"] = {year: MONTHLY_CHARGE * 12}
            situation["people"][name] = person
            members.append(name)
        for group in groups:
            situation[group][f"{group}_{i}"] = {"members": list(members)}
        situation["marital_units"][f"marital_units_{i}"] = {"members": [parent]}
        situation["households"][f"households_{i}"]["state_name"] = {year: "CO"}
    simulation = Simulation(situation=situation)
    return [float(fee) for fee in simulation.calculate("co_ccap_parent_fee", month)]


def child(age=3, in_care=True, hours=8, days=0, week=0, rating=0):
    return dict(
        age=age, in_care=in_care, hours=hours, days=days, week=week, rating=rating
    )


months = st.sampled_from(sorted(GUIDELINES))
incomes = st.integers(min_value=0, max_value=150_000)
# Hours straddle each band edge in section 3.130(C); 0 means unknown.
daily_hours = st.sampled_from([0, 1, 4.5, 5, 5.5, 8, 12, 12.5, 16, 17, 18])
# Attending days per month; 0 means none reported.
monthly_days = st.integers(min_value=0, max_value=23)
# Scheduled days per week; 0 means none reported.
weekly_days = st.integers(min_value=0, max_value=7)
child_ages = st.integers(min_value=0, max_value=12)
any_children = st.builds(
    child,
    age=child_ages,
    in_care=st.booleans(),
    hours=daily_hours,
    days=monthly_days,
    week=weekly_days,
    rating=st.integers(min_value=0, max_value=5),
)


@settings(max_examples=25, deadline=None)
# The Department's tool: $40,000, a family of 3 and 2 children, full time.
@example(month="2026-01", income=40_000, children=[child(), child(age=5)])
@example(month="2026-10", income=40_000, children=[child(), child(age=5)])
# $1,199 a year gives a base fee of $0.99917, which drops to $0.
@example(month="2026-01", income=1_199, children=[child()])
# $21,500 for two gives a base fee of exactly $22.
@example(month="2026-01", income=21_500, children=[child()])
# Income at the guideline adds nothing for the second child.
@example(month="2026-01", income=26_650, children=[child(), child()])
# 13 days of 8 hours make 13 units, full time; 12 days make 12, part time.
@example(month="2026-01", income=60_000, children=[child(days=13), child(days=12)])
# 12 attending days beat a two-day week (8.67 days): 12 units, part time.
# A three-day week (13 days) beats 10 attending days: 13 units, full time.
@example(month="2026-01", income=60_000, children=[child(week=2, days=12)])
@example(month="2026-01", income=60_000, children=[child(week=3, days=10)])
# A 6-year-old with 5-hour days is part time under (W) at 24 days; a
# 5-year-old with the same days has 13.2 units, full time.
@example(month="2026-01", income=30_000, children=[child(age=6, hours=5, days=24)])
@example(month="2026-01", income=30_000, children=[child(age=5, hours=5, days=24)])
# The part-time rate, then the quality discount.
@example(month="2026-01", income=28_020, children=[child(hours=4, rating=3)])
# A child outside care with a top-rated provider.
@example(
    month="2026-01",
    income=50_000,
    children=[child(hours=4), child(age=9, in_care=False, rating=5)],
)
@given(
    month=months,
    income=incomes,
    children=st.lists(any_children, min_size=1, max_size=4),
)
def test_the_fee_matches_an_independent_implementation(month, income, children):
    (fee,) = fees(month, [{"income": income, "children": children}])
    expected = float(reference_fee(month, income, children))
    assert fee == pytest.approx(expected, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(month="2026-01", income=0, loss=-20_000, children=[child()])
@example(month="2028-10", income=150_000, loss=0, children=[child(), child()])
@given(
    month=st.sampled_from(["2026-01", "2026-10", "2028-10"]),
    income=incomes,
    loss=st.integers(min_value=-50_000, max_value=0),
    children=st.lists(any_children, min_size=1, max_size=4),
)
def test_the_fee_is_never_negative_and_in_whole_dollars(month, income, loss, children):
    household = {"income": income, "loss": loss, "children": children}
    (fee,) = fees(month, [household])
    assert fee >= 0
    assert fee == pytest.approx(round(fee), abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(month="2026-01", income=40_000, ages=[3, 5])
@example(month="2026-01", income=20_000, ages=[3, 5, 8])
# The guideline for four from October 2026 is $33,000.
@example(month="2026-10", income=33_000, ages=[1, 2, 3])
@example(month="2026-10", income=33_001, ages=[1, 2, 3])
@given(
    month=months,
    income=incomes,
    ages=st.lists(child_ages, min_size=2, max_size=4),
)
def test_each_additional_child_in_care_adds_15_dollars_above_the_guideline(
    month, income, ages
):
    # The same household with 0, 1, ... of its children in full-time care.
    households = [
        {
            "income": income,
            "children": [
                child(age=age, in_care=j < count) for j, age in enumerate(ages)
            ],
        }
        for count in range(len(ages) + 1)
    ]
    result = fees(month, households)
    above = income > guideline(month, ages)
    assert result[0] == 0
    for count in range(1, len(ages) + 1):
        added = 15 * (count - 1) if above else 0
        assert result[count] - result[1] == pytest.approx(added, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(month="2026-01", income=40_000, children=[child(hours=4), child(hours=4)])
@example(month="2026-01", income=40_000, children=[child(hours=4), child(hours=8)])
@example(month="2026-01", income=30_000, children=[child(age=8, hours=4, days=24)])
@given(
    month=months,
    income=incomes,
    children=st.lists(
        st.builds(
            child,
            age=child_ages,
            hours=daily_hours,
            days=monthly_days,
            week=weekly_days,
        ),
        min_size=1,
        max_size=4,
    ),
)
def test_the_part_time_rate_applies_only_when_every_child_in_care_is_part_time(
    month, income, children
):
    full_time = [dict(child, hours=8, days=0, week=0) for child in children]
    fee, full_time_fee = fees(
        month,
        [
            {"income": income, "children": children},
            {"income": income, "children": full_time},
        ],
    )
    if all(part_time(child) for child in children):
        expected = floor(Decimal(round(full_time_fee)) * Decimal("0.55"))
    else:
        expected = full_time_fee
    assert fee == pytest.approx(float(expected), abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(month="2026-01", income=40_000, children=[child(), child()], rating=3)
@example(month="2026-01", income=40_000, children=[child(hours=4)], rating=2)
@example(
    month="2026-01",
    income=28_020,
    children=[child(hours=4), child(age=10, in_care=False)],
    rating=5,
)
@given(
    month=months,
    income=incomes,
    children=st.lists(any_children, min_size=1, max_size=4),
    rating=st.integers(min_value=0, max_value=5),
)
def test_a_top_three_provider_cuts_the_fee_by_20_percent(
    month, income, children, rating
):
    unrated = [dict(child, rating=0) for child in children]
    # Make sure a child is in care, and give that child the rating.
    unrated[0]["in_care"] = True
    rated = [dict(child) for child in unrated]
    rated[0]["rating"] = rating
    # The same rating for each child outside care instead.
    outside = [
        dict(child, rating=0 if child["in_care"] else rating) for child in unrated
    ]
    unrated_fee, rated_fee, outside_fee = fees(
        month,
        [
            {"income": income, "children": unrated},
            {"income": income, "children": rated},
            {"income": income, "children": outside},
        ],
    )
    if rating >= 3:
        expected = floor(Decimal(round(unrated_fee)) * Decimal("0.8"))
    else:
        expected = unrated_fee
    assert rated_fee == pytest.approx(float(expected), abs=TOLERANCE)
    assert outside_fee == pytest.approx(unrated_fee, abs=TOLERANCE)
