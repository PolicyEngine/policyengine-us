"""Colorado's Child Care Assistance Program charges each household one parent fee.

8 CCR 1403-1 section 3.124 (ruleVersionId 12658, PDF pages 79-85) builds the
fee from gross countable income and household size. Through July 2028 counties
charge 1% of income plus 14% of income above the federal poverty guideline
((P)(1) and (P)(2)), and $15 for each child in care after the first when income
exceeds the guideline ((P)(3)). From August 2028 they charge marginal rates of
1%, 3%, 5% and 7% ((Q)). The fee comes in whole dollars ((A)), at 55% when every
child in care receives part-time care ((U) and (W)), and 20% lower at a provider
in the top three quality levels ((H)). The Department's parent fee tool drops
the cents after each step.

Invariants, which these tests check on generated households:

1. The fee never falls below zero and always comes to whole dollars.
2. Through July 2028, at a given income and household size, each child in
   full-time care after the first adds $15 to the fee at a provider below
   quality level 3 when income exceeds the guideline, and nothing when it does
   not.
3. At a provider below quality level 3, the fee falls to 55% of the full-time
   fee, without cents, when every child in care receives part-time care, and
   stays at the full-time fee when any child in care receives full-time care.
4. A provider in the top three quality levels, for any child in care, cuts the
   fee by 20% without cents. A lower rating, or a rating for a child outside
   care, changes nothing.

A differential test compares the model with `reference_fee`, written from the
rule in exact decimal arithmetic, in January and October 2026 and in July and
August 2028, on incomes in whole dollars and in cents. The reference uses the
model's schedule defaults and, for 2028, its projected guideline.
"""

from decimal import ROUND_FLOOR, ROUND_HALF_EVEN, Decimal

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
CENT = Decimal("0.01")
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
# Section 3.124(Q) applies from this month.
FIRST_MONTH_OF_MARGINAL_RATES = "2028-08"
# Without a schedule, the model reads care on each weekday.
ASSUMED_DAYS_PER_WEEK = Decimal(5)
ASSUMED_DAYS_PER_MONTH = ASSUMED_DAYS_PER_WEEK * 52 / 12


def floor(amount):
    return amount.to_integral_value(rounding=ROUND_FLOOR)


def in_cents(amount):
    return amount.quantize(CENT, rounding=ROUND_HALF_EVEN)


def monthly_income(annual_income):
    return in_cents(max(Decimal(annual_income), Decimal(0)) / 12)


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


def care_hours(child):
    """Reported daily hours, or weekly hours over the child's days of care."""
    if child["hours"]:
        return Decimal(str(child["hours"]))
    reported_days = max(Decimal(child["week"]), Decimal(child["days"]) * 12 / 52)
    days_in_a_week = reported_days or ASSUMED_DAYS_PER_WEEK
    return Decimal(str(child["weekly"])) / days_in_a_week


def part_time(child):
    """Fewer than 13 units a month (3.124(U)), or up to 5 hours a day for a
    child in grades 1 to 12 (3.124(W)). PolicyEngine has no grade input, so a
    child in school (ages 5 to 17) aged 6 or older counts as in grade 1 or
    above, as in the model, and such a child whose only reported care is an
    after-school expense counts as in part-time care. Days of care come from
    the larger of days a week x 52 / 12 and attending days a month, as in the
    model."""
    hours = care_hours(child)
    scheduled_days = Decimal(child["week"] * 52) / 12
    days = max(scheduled_days, Decimal(child["days"])) or ASSUMED_DAYS_PER_MONTH
    in_grade_one_or_above = 6 <= child["age"] <= 17
    no_schedule = hours == 0 and child["week"] == 0 and child["days"] == 0
    after_school_only = child["after_school"] and no_schedule
    return daily_units(hours) * days < 13 or (
        in_grade_one_or_above and (0 < hours <= 5 or after_school_only)
    )


def guideline(month, children):
    """The monthly guideline in cents for a parent and these children."""
    first, additional = GUIDELINES[month]
    return in_cents((first + additional * len(children)) / 12)


def marginal_fee(income, limit):
    """Section 3.124(Q): each rate applies to the income in its band."""
    bands = [
        (Decimal("0.01"), Decimal(0), limit),
        (Decimal("0.03"), limit, limit * Decimal("1.3")),
        (Decimal("0.05"), limit * Decimal("1.3"), limit * Decimal("1.6")),
    ]
    fee = sum(rate * max(min(income, upper) - lower, 0) for rate, lower, upper in bands)
    return fee + Decimal("0.07") * max(income - limit * Decimal("1.6"), 0)


def reference_fee(month, annual_income, children, limit):
    """Section 3.124, step by step, dropping cents as the Department's tool does."""
    in_care = [child for child in children if child["in_care"]]
    if not in_care:
        return Decimal(0)
    income = monthly_income(annual_income)
    if month >= FIRST_MONTH_OF_MARGINAL_RATES:
        base = marginal_fee(income, limit)
        add_on = 0
    else:
        base = income * Decimal("0.01") + max(income - limit, 0) * Decimal("0.14")
        add_on = 15 * (len(in_care) - 1) if income > limit else 0
    fee = floor(base + add_on)
    if all(part_time(child) for child in in_care):
        fee = floor(fee * Decimal("0.55"))
    if max(child["rating"] for child in in_care) >= 3:
        fee = floor(fee * Decimal("0.8"))
    return fee


def simulate(month, households):
    """One simulation of these households.

    Each household holds one parent and the given children. A child in care
    has the given schedule and a monthly charge, after school if the child
    says so; a child outside care has neither."""
    year = int(month[:4])
    groups = ("tax_units", "spm_units", "families", "marital_units", "households")
    situation = {"people": {}, **{group: {} for group in groups}}
    for i, household in enumerate(households):
        parent = f"parent_{i}"
        members = [parent]
        situation["people"][parent] = {
            "age": {year: 35},
            "employment_income": {year: float(household["income"])},
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
                if child["weekly"]:
                    person["childcare_hours_per_week"] = {year: child["weekly"]}
                charge = {year: MONTHLY_CHARGE * 12}
                if child["after_school"]:
                    person["after_school_expenses"] = charge
                else:
                    person["pre_subsidy_childcare_expenses"] = charge
            situation["people"][name] = person
            members.append(name)
        for group in groups:
            situation[group][f"{group}_{i}"] = {"members": list(members)}
        situation["marital_units"][f"marital_units_{i}"] = {"members": [parent]}
        situation["households"][f"households_{i}"]["state_name"] = {year: "CO"}
    return Simulation(situation=situation)


def fees(month, households):
    """The model's fee for each household, from one simulation."""
    simulation = simulate(month, households)
    return [float(fee) for fee in simulation.calculate("co_ccap_parent_fee", month)]


def child(
    age=3, in_care=True, hours=8, days=0, week=0, rating=0, weekly=0, after_school=False
):
    return dict(
        age=age,
        in_care=in_care,
        hours=hours,
        days=days,
        week=week,
        rating=rating,
        weekly=weekly,
        after_school=after_school,
    )


months = st.sampled_from(sorted(GUIDELINES))
# Either side of the switch to section 3.124(Q), as well as the published months.
months_through_2028 = st.sampled_from([*sorted(GUIDELINES), "2028-07", "2028-08"])
incomes = st.integers(min_value=0, max_value=150_000)
# Twelve times a monthly amount in cents, so the month comes to whole cents.
incomes_in_cents = st.integers(min_value=0, max_value=1_250_000).map(
    lambda cents: Decimal(cents) * 12 / 100
)
# Hours straddle each band edge in section 3.130(C); 0 means unknown.
daily_hours = st.sampled_from([0, 0, 0, 1, 4.5, 5, 5.5, 8, 12, 12.5, 16, 17, 18])
# Weekly hours count only when daily hours are unknown; 0 means none reported.
weekly_hours = st.sampled_from([0, 10, 15, 20, 25, 36, 40, 60])
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
    weekly=weekly_hours,
    after_school=st.booleans(),
)


@settings(max_examples=25, deadline=None)
# The Department's tool formula: $40,000, a family of 3 and 2 children, full time.
@example(month="2026-01", income=40_000, children=[child(), child(age=5)])
@example(month="2026-10", income=40_000, children=[child(), child(age=5)])
# $1,199 a year gives a base fee of $0.9992, which drops to $0.
@example(month="2026-01", income=1_199, children=[child()])
# $21,500 for two gives a base fee just above $22.
@example(month="2026-01", income=21_500, children=[child()])
# $23,999.64 gives $19.9997, and $11,999.64 gives $9.9997: each drops a dollar.
@example(month="2026-01", income=Decimal("23999.64"), children=[child(), child()])
@example(month="2026-01", income=Decimal("11999.64"), children=[child()])
# $21,180 for two gives a fee of exactly $18, which float64 arithmetic takes to
# $17.9999999999999.
@example(month="2026-01", income=21_180, children=[child()])
# $26,713.32 for three gives $23.0003 on the guideline in cents, $2,220.83.
# Unrounded, the guideline of $2,220.8333 would give $22.9998.
@example(month="2026-01", income=Decimal("26713.32"), children=[child(), child()])
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
# $28,056 for two gives a base fee of $103.95, which drops to $103 before the
# part-time rate: 55% of $103 comes to $56.65, so $56.
@example(month="2026-01", income=28_056, children=[child(hours=4)])
# A child outside care with a top-rated provider.
@example(
    month="2026-01",
    income=50_000,
    children=[child(hours=4), child(age=9, in_care=False, rating=5)],
)
# 20 hours a week over five weekdays: 4 hours a day, 11.92 units, part time.
@example(month="2026-01", income=40_000, children=[child(hours=0, weekly=20)])
# 20 hours a week over two days: 10 hours a day, 8.67 units, part time.
@example(month="2026-01", income=40_000, children=[child(hours=0, weekly=20, week=2)])
# 40 hours a week over five weekdays: 8 hours a day, full time.
@example(month="2026-01", income=40_000, children=[child(hours=0, weekly=40)])
# 15 hours a week over 13 attending days (three a week): 5 hours a day.
@example(month="2026-01", income=40_000, children=[child(hours=0, weekly=15, days=13)])
# 20 attending days give more days a week (4.62) than a two-day week: 4.33 hours
# a day, 11 units, part time.
@example(
    month="2026-01",
    income=40_000,
    children=[child(hours=0, weekly=20, week=2, days=20)],
)
# An 8-year-old with only after-school expenses receives part-time care; a
# 4-year-old with the same expense has no school day to fit it around.
@example(
    month="2026-01",
    income=40_000,
    children=[child(age=8, hours=0, after_school=True)],
)
@example(
    month="2026-01",
    income=40_000,
    children=[child(age=4, hours=0, after_school=True)],
)
# The switch to section 3.124(Q).
@example(month="2028-07", income=60_000, children=[child(), child()])
@example(month="2028-08", income=60_000, children=[child(), child()])
@given(
    month=months_through_2028,
    income=st.one_of(incomes, incomes_in_cents),
    children=st.lists(any_children, min_size=1, max_size=4),
)
def test_the_fee_matches_an_independent_implementation(month, income, children):
    simulation = simulate(month, [{"income": income, "children": children}])
    fee = float(simulation.calculate("co_ccap_parent_fee", month)[0])
    if month in GUIDELINES:
        limit = guideline(month, children)
    else:
        limit = in_cents(Decimal(float(simulation.calculate("co_ccap_fpg", month)[0])))
    expected = float(reference_fee(month, income, children, limit))
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
    above = monthly_income(income) > guideline(month, ages)
    assert result[0] == 0
    for count in range(1, len(ages) + 1):
        added = 15 * (count - 1) if above else 0
        assert result[count] - result[1] == pytest.approx(added, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(month="2026-01", income=40_000, children=[child(hours=4), child(hours=4)])
@example(month="2026-01", income=40_000, children=[child(hours=4), child(hours=8)])
@example(month="2026-01", income=30_000, children=[child(age=8, hours=4, days=24)])
@example(month="2026-01", income=40_000, children=[child(hours=0, weekly=20)])
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
            weekly=weekly_hours,
            after_school=st.booleans(),
        ),
        min_size=1,
        max_size=4,
    ),
)
def test_the_part_time_rate_applies_only_when_every_child_in_care_is_part_time(
    month, income, children
):
    full_time = [
        dict(child, hours=8, days=0, week=0, weekly=0, after_school=False)
        for child in children
    ]
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
