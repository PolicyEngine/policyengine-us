"""Properties of the self-employed SEP, SIMPLE and qualified plan deduction limit.

A self-employed person's plan compensation is earned income under 26 U.S.C.
401(c)(2), which is net of the deductible part of self-employment tax and of
the plan deduction itself, and 404(a)(8)(C) caps the deduction at that earned
income before the plan deduction. IRS Publication 560 turns this into the
Deduction Worksheet for Self-Employed (2025 edition, page 39). The model's
single input does not say which plan the person has, so the model's limit is
the worksheet's largest total over the elective deferrals and catch-up
contributions the person could still make (`self_employed_pension_contribution_limit`).

The plan may be established under the Schedule C business, the Schedule F
farm or a partnership (K-1 box 14 code A), and step 1 is the net profit of the
plan's business (`self_employed_pension_plan_business`). By default every
profitable business has a plan, under one dollar limit and one elective
deferral limit, and their earned income adds up.

The reference below runs the worksheet's steps literally, with the IRS's
published dollar amounts rather than model parameters, and takes the largest
step 19 over a grid of elective deferrals (step 9) and catch-up contributions
(step 17). Only Schedule 1 line 15, the deductible part of self-employment
tax, comes from the model. Hypothesis draws batches of single filers across
three years, and each batch runs as one vectorized simulation in which every
filer appears once for each plan business. For every person and year:

1. The limit equals the worksheet maximum, and step 3 equals the plan
   businesses' net profit less their share of line 15, split by net profit
   as on Form 7206 lines 5 to 8.
2. The deduction is min(desired contributions, limit), is at most earned
   income (404(a)(8)(C)), which is at most the plan businesses' net profit,
   and is at most the dollar limit plus the person's catch-up amount.
3. For a filer whose only income is self-employment profit, AGI is never
   negative when no business has a loss.
4. Across plan businesses: the default's earned income is the sum of the
   named businesses' earned income; its limit is at least each named
   business's limit, so naming no business never lowers the deduction from
   a plan under the Schedule C business alone, and at most their sum.

A deterministic grid checks that the limit rises with Schedule C profit and
with farm profit, and falls with deferrals to an employer's plan.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
# Plan contribution rate: 26 U.S.C. 404(a)(3)(A)(i)(I) and 404(h)(1)(C).
PLAN_RATE = 0.25
# Model outputs are float32, whose spacing exceeds a cent above $131,072.
RTOL = 1e-6
# Businesses under which the plan may be established; ALL is the default.
PLAN_BUSINESSES = ["ALL", "SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP"]
# Published amounts: IRS Notices 2021-61 (2022), 2024-80 (2025) and 2025-67
# (2026); section 414(v)(2)(E) for ages 60 to 63 from 2025.
PUBLISHED = {
    2022: dict(
        annual_additions=61_000,
        compensation_limit=305_000,
        deferral=20_500,
        catch_up=6_500,
        catch_up_60_to_63=6_500,
    ),
    2025: dict(
        annual_additions=70_000,
        compensation_limit=350_000,
        deferral=23_500,
        catch_up=7_500,
        catch_up_60_to_63=11_250,
    ),
    2026: dict(
        annual_additions=72_000,
        compensation_limit=360_000,
        deferral=24_500,
        catch_up=8_000,
        catch_up_60_to_63=11_250,
    ),
}
YEARS = list(PUBLISHED)


def catch_up_amount(year, age):
    amounts = PUBLISHED[year]
    return np.select(
        [age < 50, (age >= 60) & (age <= 63)],
        [0, amounts["catch_up_60_to_63"]],
        amounts["catch_up"],
    )


def worksheet_step_19(step_3, deferrals, catch_up, amounts):
    """Pub. 560 Deduction Worksheet for Self-Employed, steps 4 to 19."""
    step_4 = PLAN_RATE / (1 + PLAN_RATE)  # Rate Table: 25% -> 0.2
    step_5 = step_3 * step_4
    step_6 = amounts["compensation_limit"] * PLAN_RATE
    step_7 = np.minimum(step_5, step_6)
    step_8 = amounts["annual_additions"]
    step_9 = deferrals
    step_10 = step_8 - step_9
    step_11 = step_3 - step_9
    step_12 = step_11 / 2
    step_13 = np.minimum(np.minimum(step_7, step_10), step_12)
    step_14 = step_3 - step_13
    step_15 = np.minimum(step_9, step_14)
    step_16 = step_14 - step_15
    step_18 = np.minimum(step_16, catch_up)
    with_deferrals = step_13 + step_15 + step_18
    # Without elective deferrals the worksheet skips to step 21.
    without_deferrals = np.minimum(step_7, step_8)
    return np.where((deferrals > 0) | (catch_up > 0), with_deferrals, without_deferrals)


def worksheet_maximum(step_3, regular_room, catch_up_room, amounts, points=41):
    """Largest step 19 over deferrals and catch-up contributions in their room."""
    best = np.zeros_like(step_3)
    for d, c in itertools.product(np.linspace(0, 1, points), repeat=2):
        # A deferral can't exceed compensation, so the grid stops at step 3.
        deferrals = d * np.minimum(regular_room, step_3)
        catch_up = c * catch_up_room
        best = np.maximum(best, worksheet_step_19(step_3, deferrals, catch_up, amounts))
    return best


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(people_inputs):
    people, tax_units, households = {}, {}, {}
    for i, inputs in enumerate(people_inputs):
        name = f"p{i}"
        people[name] = {variable: every_year(v) for variable, v in inputs.items()}
        # The partnership's earnings also enter gross income.
        people[name]["partnership_income"] = every_year(
            inputs.get("partnership_self_employment_net_earnings", 0)
        )
        tax_units[f"t{i}"] = {"members": [name]}
        households[f"h{i}"] = {"members": [name], "state_code": every_year("TX")}
    return {"people": people, "tax_units": tax_units, "households": households}


def column(people_inputs, variable):
    return np.array([p.get(variable, 0) for p in people_inputs], dtype=float)


def plan_business_profit(people_inputs):
    """Step 1: the net profit of the businesses under which the plan is established."""
    profits = {
        "SCHEDULE_C": np.maximum(
            column(people_inputs, "self_employment_income")
            + column(people_inputs, "sstb_self_employment_income"),
            0,
        ),
        "SCHEDULE_F": np.maximum(column(people_inputs, "farm_operations_income"), 0),
        "PARTNERSHIP": np.maximum(
            column(people_inputs, "partnership_self_employment_net_earnings"), 0
        ),
    }
    all_profits = sum(profits.values())
    plan_business = np.array([p["plan_business"] for p in people_inputs])
    plan_profit = np.select(
        [plan_business == business for business in profits],
        list(profits.values()),
        all_profits,
    )
    return plan_profit, all_profits


def reference(sim, people_inputs, year):
    amounts = PUBLISHED[year]
    age = column(people_inputs, "age")
    plan_profit, all_profits = plan_business_profit(people_inputs)
    share = np.divide(
        plan_profit,
        all_profits,
        out=np.zeros_like(plan_profit),
        where=all_profits > 0,
    )
    # Step 2 is the one model output the reference takes as given.
    step_2 = sim.calculate("self_employment_tax_ald_person", year) * share
    step_3 = np.maximum(plan_profit - step_2, 0)
    # Section 402(g) room left by deferrals to an employer's plan, which use
    # the regular limit first.
    catch_up = catch_up_amount(year, age)
    deferral_limit = amounts["deferral"] + catch_up
    desired = column(people_inputs, "traditional_401k_contributions_desired") + column(
        people_inputs, "roth_401k_contributions_desired"
    )
    room = deferral_limit - np.minimum(desired, deferral_limit)
    catch_up_room = np.minimum(room, catch_up)
    regular_room = room - catch_up_room
    limit = worksheet_maximum(step_3, regular_room, catch_up_room, amounts)
    return plan_profit, step_3, limit, catch_up


def close(actual, expected, message):
    np.testing.assert_allclose(
        actual, expected, rtol=RTOL, atol=TOLERANCE, err_msg=message
    )


def at_most(actual, bound):
    return np.all(actual <= bound + TOLERANCE + RTOL * np.abs(bound))


def check(sim, people_inputs):
    desired = column(people_inputs, "self_employed_pension_contributions_desired")
    self_employment_only = np.array([p["self_employment_only"] for p in people_inputs])
    no_losses = (
        (
            column(people_inputs, "self_employment_income")
            + column(people_inputs, "sstb_self_employment_income")
            >= 0
        )
        & (column(people_inputs, "farm_operations_income") >= 0)
        & (column(people_inputs, "partnership_self_employment_net_earnings") >= 0)
    )
    for year in YEARS:
        plan_profit, step_3, expected, catch_up = reference(sim, people_inputs, year)
        earned_income = sim.calculate("self_employed_pension_earned_income", year)
        limit = sim.calculate("self_employed_pension_contribution_limit", year)
        deduction = sim.calculate("self_employed_pension_contribution_ald_person", year)
        message = f"year {year}"
        # 1. The worksheet.
        close(earned_income, step_3, message)
        close(limit, expected, message)
        # 2. Bounds.
        close(deduction, np.minimum(desired, limit), message)
        assert np.all(deduction >= 0), message
        assert at_most(deduction, earned_income), message
        assert at_most(earned_income, plan_profit), message
        cap = PUBLISHED[year]["annual_additions"] + catch_up
        assert at_most(limit, cap), message
        # 3. AGI from self-employment profit alone.
        agi = sim.calculate("adjusted_gross_income", year)
        rows = self_employment_only & no_losses
        assert np.all(agi[rows] >= -TOLERANCE), (message, agi[rows])


def check_across_plan_businesses(sim, people_inputs):
    """Property 4, for filers laid out by every_plan_business."""
    width = len(PLAN_BUSINESSES)
    for year in YEARS:
        message = f"year {year}"
        earned, limits, deductions = (
            sim.calculate(variable, year).reshape(-1, width)
            for variable in (
                "self_employed_pension_earned_income",
                "self_employed_pension_contribution_limit",
                "self_employed_pension_contribution_ald_person",
            )
        )
        # Column 0 is the default (every profitable business), column 1 the
        # Schedule C business alone.
        close(earned[:, 0], earned[:, 1:].sum(axis=1), message)
        assert at_most(limits[:, 1:].max(axis=1), limits[:, 0]), message
        assert at_most(deductions[:, 1], deductions[:, 0]), message
        assert at_most(limits[:, 0], limits[:, 1:].sum(axis=1)), message


profits = st.one_of(
    st.sampled_from([0, 400, 433, 434, 2_000, 20_000, 30_000, 200_000, 500_000]),
    st.integers(-20_000, 600_000),
)
smaller = st.one_of(st.just(0), st.integers(-10_000, 150_000))
contributions = st.one_of(st.sampled_from([0, 1_000_000]), st.integers(0, 100_000))
person_strategy = st.fixed_dictionaries(
    {
        "self_employment_only": st.booleans(),
        "age": st.sampled_from([30, 49, 50, 55, 59, 60, 63, 64, 70]),
        "self_employment_income": profits,
        "sstb_self_employment_income": st.one_of(st.just(0), profits),
        "farm_operations_income": smaller,
        "partnership_self_employment_net_earnings": st.one_of(st.just(0), smaller),
        "employment_income": st.one_of(st.just(0), st.integers(0, 250_000)),
        "traditional_401k_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 40_000)
        ),
        "roth_401k_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 20_000)
        ),
        "self_employed_pension_contributions_desired": contributions,
    }
)


def normalize(person):
    person = dict(person)
    if person["self_employment_only"]:
        for variable in (
            "employment_income",
            "traditional_401k_contributions_desired",
            "roth_401k_contributions_desired",
        ):
            person[variable] = 0
    return person


def every_plan_business(people_inputs):
    """Each filer once for each plan business, in the order of PLAN_BUSINESSES."""
    return [
        dict(person, plan_business=business)
        for person in people_inputs
        for business in PLAN_BUSINESSES
    ]


def simulation_inputs(people_inputs):
    return [
        {
            **{
                k: float(v)
                for k, v in p.items()
                if k not in ("self_employment_only", "plan_business")
            },
            "self_employed_pension_plan_business": p["plan_business"],
        }
        for p in people_inputs
    ]


SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(person_strategy.map(normalize), min_size=2, max_size=8))
def test_limit_matches_the_pub_560_worksheet(people_inputs):
    people_inputs = every_plan_business(people_inputs)
    sim = Simulation(situation=build_situation(simulation_inputs(people_inputs)))
    check(sim, people_inputs)
    check_across_plan_businesses(sim, people_inputs)


GRID_PROFITS = [
    -1_000,
    0,
    434,
    5_000,
    20_000,
    30_000,
    60_000,
    100_000,
    200_000,
    600_000,
]
GRID_DEFERRALS = [0, 10_000, 23_500, 40_000]


@pytest.fixture(scope="module")
def grid():
    people_inputs = [
        {
            "self_employment_only": False,
            "plan_business": "ALL",
            "age": 55,
            "self_employment_income": profit,
            "employment_income": 50_000,
            "traditional_401k_contributions_desired": deferrals,
            "self_employed_pension_contributions_desired": 1_000_000,
        }
        for deferrals, profit in itertools.product(GRID_DEFERRALS, GRID_PROFITS)
    ]
    sim = Simulation(situation=build_situation(simulation_inputs(people_inputs)))
    return sim, people_inputs


@pytest.mark.parametrize("year", YEARS)
def test_grid_matches_the_worksheet_and_is_monotone(grid, year):
    sim, people_inputs = grid
    check(sim, people_inputs)
    limit = sim.calculate("self_employed_pension_contribution_limit", year).reshape(
        len(GRID_DEFERRALS), len(GRID_PROFITS)
    )
    # The limit rises with Schedule C profit...
    assert np.all(np.diff(limit, axis=1) >= -TOLERANCE)
    # ...and falls as deferrals to an employer's plan use up the room.
    assert np.all(np.diff(limit, axis=0) <= TOLERANCE)
    # No room left: steps 7 and 8, the SEP and profit-sharing limit.
    earned_income = sim.calculate("self_employed_pension_earned_income", year)
    no_room = earned_income.reshape(limit.shape)[-1]
    np.testing.assert_allclose(
        limit[-1],
        np.minimum(PUBLISHED[year]["annual_additions"], 0.2 * no_room),
        atol=TOLERANCE,
    )


GRID_FARM_PROFITS = [0, 1_000, 5_000, 20_000, 60_000, 200_000, 600_000]


@pytest.mark.parametrize("year", YEARS)
def test_limit_rises_with_farm_profit(year):
    """A profitable farm adds to the default plan's earned income."""
    people_inputs = [
        {
            "self_employment_only": True,
            "plan_business": "ALL",
            "age": 45,
            "self_employment_income": 20_000,
            "farm_operations_income": farm,
            "self_employed_pension_contributions_desired": 1_000_000,
        }
        for farm in GRID_FARM_PROFITS
    ]
    sim = Simulation(situation=build_situation(simulation_inputs(people_inputs)))
    check(sim, people_inputs)
    earned_income = sim.calculate("self_employed_pension_earned_income", year)
    limit = sim.calculate("self_employed_pension_contribution_limit", year)
    assert np.all(np.diff(earned_income) > 0)
    assert np.all(np.diff(limit) >= -TOLERANCE)
