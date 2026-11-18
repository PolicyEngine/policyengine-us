"""Properties of the self-employed SEP, SIMPLE and qualified plan deduction limit.

A self-employed person's plan compensation is earned income under 26 U.S.C.
401(c)(2), which is net of the deductible part of self-employment tax and of
the plan deduction itself, and 404(a)(8)(C) caps the deduction at that earned
income before the plan deduction. IRS Publication 560 turns this into the
Deduction Worksheet for Self-Employed (2025 edition, page 39). The model's
single input does not say which plan the person has, so the model's limit is
the worksheet's largest total over the elective deferrals and catch-up
contributions the person could still make (`self_employed_pension_contribution_limit`).

The reference below runs worksheet steps 4 to 19 literally, with the IRS's
published dollar amounts rather than model parameters, and takes the largest
step 19 over a grid of elective deferrals (step 9) and catch-up contributions
(step 17). Schedule 1 line 15 is computed here from Schedule SE with the
published wage bases, and step 2 is Schedule C's share of it, split by net
profit as on Form 7206 lines 5 to 8. Hypothesis draws batches of single filers
across three years, and each batch runs as one vectorized simulation. For
every person and year:

1. Line 15 equals half of the Schedule SE tax, the limit equals the worksheet
   maximum, and step 3 equals Schedule C net profit less step 2.
2. The deduction is min(desired contributions, limit), is at most earned
   income (404(a)(8)(C)), which is at most Schedule C net profit, and is at
   most the dollar limit plus the person's catch-up amount, which is all
   414(v)(3)(A) puts outside 415(c).
3. For a filer whose only income is Schedule C profit, AGI is never negative
   when the profit is not, because the deduction is at most profit less line
   15.

A deterministic grid checks, at its points, that the limit rises with Schedule
C profit (it dips just past $433 of profit, where self-employment tax starts)
and falls as deferrals to an employer's plan use up the room.

The model computes in float32, so comparisons allow a relative error of 1e-6
on top of the $0.01 tolerance.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
RTOL = 1e-6
# Plan contribution rate: 26 U.S.C. 404(a)(3)(A)(i)(I) and 404(h)(1)(C).
PLAN_RATE = 0.25
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

# Schedule SE, as test data rather than model parameters.
# 26 U.S.C. 1402(a)(12): net earnings are 92.35% of net profit.
NET_EARNINGS_SHARE = 0.9235
# 26 U.S.C. 1402(b)(2): no net earnings below $400.
NET_EARNINGS_EXEMPTION = 400
# 26 U.S.C. 1401(a) and (b).
SOCIAL_SECURITY_RATE = 0.124
MEDICARE_RATE = 0.029
# Contribution and benefit bases, https://www.ssa.gov/oact/cola/cbb.html.
WAGE_BASE = {2022: 147_000, 2025: 176_100, 2026: 184_500}


def schedule_se_deduction(year, net_profit, wages):
    """Schedule 1 line 15: half of Schedule SE self-employment tax."""
    net_earnings = net_profit * NET_EARNINGS_SHARE
    net_earnings = np.where(net_earnings < NET_EARNINGS_EXEMPTION, 0, net_earnings)
    social_security_room = np.maximum(WAGE_BASE[year] - wages, 0)
    tax = SOCIAL_SECURITY_RATE * np.minimum(
        net_earnings, social_security_room
    ) + MEDICARE_RATE * np.maximum(net_earnings, 0)
    return tax / 2


def close(actual, expected, message):
    np.testing.assert_allclose(
        actual, expected, rtol=RTOL, atol=TOLERANCE, err_msg=message
    )


def at_most(actual, bound):
    return np.all(actual <= bound + TOLERANCE + RTOL * np.abs(bound))


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
        tax_units[f"t{i}"] = {"members": [name]}
        households[f"h{i}"] = {"members": [name], "state_code": every_year("TX")}
    return {"people": people, "tax_units": tax_units, "households": households}


def column(people_inputs, variable):
    return np.array([p.get(variable, 0) for p in people_inputs], dtype=float)


def reference(sim, people_inputs, year):
    amounts = PUBLISHED[year]
    age = column(people_inputs, "age")
    schedule_c = np.maximum(
        column(people_inputs, "self_employment_income")
        + column(people_inputs, "sstb_self_employment_income"),
        0,
    )
    others = np.maximum(
        column(people_inputs, "farm_operations_income"), 0
    ) + np.maximum(column(people_inputs, "partnership_self_employment_net_earnings"), 0)
    share = np.divide(
        schedule_c,
        schedule_c + others,
        out=np.zeros_like(schedule_c),
        where=schedule_c + others > 0,
    )
    # Schedule 1 line 15 from Schedule SE; step 2 is Schedule C's share.
    net_profit = (
        column(people_inputs, "self_employment_income")
        + column(people_inputs, "sstb_self_employment_income")
        + column(people_inputs, "farm_operations_income")
        + column(people_inputs, "partnership_self_employment_net_earnings")
    )
    line_15 = schedule_se_deduction(
        year, net_profit, column(people_inputs, "employment_income")
    )
    step_2 = line_15 * share
    step_3 = np.maximum(schedule_c - step_2, 0)
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
    return schedule_c, line_15, step_3, limit, catch_up


def check(sim, people_inputs, years=YEARS):
    desired = column(people_inputs, "self_employed_pension_contributions_desired")
    schedule_c_only = np.array([p["schedule_c_only"] for p in people_inputs])
    for year in years:
        schedule_c, line_15, step_3, expected, catch_up = reference(
            sim, people_inputs, year
        )
        earned_income = sim.calculate("self_employed_pension_earned_income", year)
        limit = sim.calculate("self_employed_pension_contribution_limit", year)
        deduction = sim.calculate("self_employed_pension_contribution_ald_person", year)
        message = f"year {year}"
        # 1. Schedule SE and the worksheet.
        close(sim.calculate("self_employment_tax_ald_person", year), line_15, message)
        close(earned_income, step_3, message)
        close(limit, expected, message)
        # 2. Bounds.
        close(deduction, np.minimum(desired, limit), message)
        assert np.all(deduction >= 0), message
        assert at_most(deduction, earned_income), message
        assert at_most(earned_income, schedule_c), message
        cap = PUBLISHED[year]["annual_additions"] + catch_up
        assert at_most(limit, cap), message
        # 3. AGI from Schedule C alone.
        agi = sim.calculate("adjusted_gross_income", year)
        net_profit = column(people_inputs, "self_employment_income") + column(
            people_inputs, "sstb_self_employment_income"
        )
        rows = schedule_c_only & (net_profit >= 0)
        assert np.all(agi[rows] >= -TOLERANCE), (message, agi[rows])


profits = st.one_of(
    st.sampled_from([0, 400, 433, 434, 2_000, 20_000, 30_000, 200_000, 500_000]),
    st.integers(-20_000, 600_000),
)
smaller = st.one_of(st.just(0), st.integers(-10_000, 150_000))
contributions = st.one_of(st.sampled_from([0, 1_000_000]), st.integers(0, 100_000))
person_strategy = st.fixed_dictionaries(
    {
        "schedule_c_only": st.booleans(),
        "age": st.sampled_from([30, 49, 50, 55, 59, 60, 63, 64, 70]),
        "self_employment_income": profits,
        "sstb_self_employment_income": st.one_of(st.just(0), profits),
        "farm_operations_income": smaller,
        "partnership_self_employment_net_earnings": st.one_of(
            st.just(0), st.integers(0, 150_000)
        ),
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
    if person["schedule_c_only"]:
        for variable in (
            "farm_operations_income",
            "partnership_self_employment_net_earnings",
            "employment_income",
            "traditional_401k_contributions_desired",
            "roth_401k_contributions_desired",
        ):
            person[variable] = 0
    return person


def simulation_inputs(people_inputs):
    return [
        {k: float(v) for k, v in p.items() if k != "schedule_c_only"}
        for p in people_inputs
    ]


SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(person_strategy.map(normalize), min_size=4, max_size=15))
def test_limit_matches_the_pub_560_worksheet(people_inputs):
    sim = Simulation(situation=build_situation(simulation_inputs(people_inputs)))
    check(sim, people_inputs)


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
            "schedule_c_only": False,
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
    check(sim, people_inputs, [year])
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
