"""Properties of the saver's credit base for self-employed plan contributions.

26 U.S.C. 25B(d)(1)(B) counts elective deferrals (section 402(g)(3)) toward the
saver's credit. Nonelective SEP and profit-sharing contributions, and the
matching contributions a self-employed person makes for themself (section
402(g)(8)), are employer contributions and do not count. The model's input,
`self_employed_pension_contributions`, is the person's whole Schedule 1 line 16
contribution and does not say which plan the person has, so
`self_employed_pension_elective_deferrals` counts it as elective deferrals
first, up to the section 402(g) room the person's deferrals to other
employers' 401(k) and 403(b) plans leave (the limit plus the person's catch-up
amount under section 414(v)).

The reference below uses the IRS's published limits rather than model
parameters. It takes from the model only amounts this change does not touch:
the IRA contributions and the line 16 contribution after its own limit.
Hypothesis draws batches of single filers across three years, and each batch
runs as one vectorized simulation. For every person and year:

1. The counted deferrals equal min(line 16 contribution, room), with
   0 <= counted <= line 16 contribution and counted <= room.
2. The person's elective deferrals across all plans stay within the 402(g)
   limit plus catch-up.
3. The credit base equals IRA contributions + employer-plan deferrals + the
   counted deferrals - distributions, floored at 0. It never exceeds the base
   that counts the whole line 16 contribution, and falls short of it by at
   most the line 16 contribution that is not counted.
4. The person's credit is between 0 and 50% of the base capped at $2,000.

A deterministic grid checks that the counted deferrals rise with the line 16
contribution and fall as deferrals to an employer's plan use up the room.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
# Published section 402(g)(1) limits and section 414(v) catch-up amounts: IRS
# Notices 2021-61 (2022), 2024-80 (2025) and 2025-67 (2026); section
# 414(v)(2)(E) raises the catch-up for ages 60 to 63 from 2025.
PUBLISHED = {
    2022: dict(deferral=20_500, catch_up=6_500, catch_up_60_to_63=6_500),
    2025: dict(deferral=23_500, catch_up=7_500, catch_up_60_to_63=11_250),
    2026: dict(deferral=24_500, catch_up=8_000, catch_up_60_to_63=11_250),
}
YEARS = list(PUBLISHED)
# Section 25B(a) and (b): the highest credit rate and the per-person cap on
# contributions.
TOP_RATE = 0.5
CONTRIBUTION_CAP = 2_000
EMPLOYER_PLAN_DEFERRALS = [
    "traditional_401k_contributions_desired",
    "roth_401k_contributions_desired",
    "traditional_403b_contributions_desired",
    "roth_403b_contributions_desired",
]


def deferral_limit(year, age):
    amounts = PUBLISHED[year]
    catch_up = np.select(
        [age < 50, (age >= 60) & (age <= 63)],
        [0, amounts["catch_up_60_to_63"]],
        amounts["catch_up"],
    )
    return amounts["deferral"] + catch_up


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(people_inputs):
    people, tax_units, households = {}, {}, {}
    for i, inputs in enumerate(people_inputs):
        name = f"p{i}"
        people[name] = {
            variable: every_year(float(value)) for variable, value in inputs.items()
        }
        tax_units[f"t{i}"] = {"members": [name]}
        households[f"h{i}"] = {"members": [name], "state_code": every_year("TX")}
    return {"people": people, "tax_units": tax_units, "households": households}


def column(people_inputs, variable):
    return np.array([p.get(variable, 0) for p in people_inputs], dtype=float)


def check(sim, people_inputs):
    age = column(people_inputs, "age")
    desired_employer_plan = sum(
        column(people_inputs, variable) for variable in EMPLOYER_PLAN_DEFERRALS
    )
    distributions = column(people_inputs, "retirement_distributions")
    for year in YEARS:
        message = f"year {year}"
        limit = deferral_limit(year, age)
        # Deferrals to employers' plans, scaled down to the limit when above it.
        employer_plan = np.minimum(desired_employer_plan, limit)
        room = limit - employer_plan
        line_16 = sim.calculate("self_employed_pension_contributions", year)
        counted = sim.calculate("self_employed_pension_elective_deferrals", year)
        ira = sim.calculate("traditional_ira_contributions", year) + sim.calculate(
            "roth_ira_contributions", year
        )
        model_employer_plan = sum(
            sim.calculate(variable.removesuffix("_desired"), year)
            for variable in EMPLOYER_PLAN_DEFERRALS
        )
        base = sim.calculate("savers_credit_qualified_contributions", year)
        credit = sim.calculate("savers_credit_person", year)

        # 1. The counted deferrals.
        assert np.all(line_16 >= 0), message
        np.testing.assert_allclose(
            model_employer_plan, employer_plan, atol=TOLERANCE, err_msg=message
        )
        np.testing.assert_allclose(
            counted, np.minimum(line_16, room), atol=TOLERANCE, err_msg=message
        )
        assert np.all(counted >= -TOLERANCE), message
        assert np.all(counted <= line_16 + TOLERANCE), message
        assert np.all(counted <= room + TOLERANCE), message
        # 2. Section 402(g) across all of the person's plans.
        assert np.all(model_employer_plan + counted <= limit + TOLERANCE), message
        # 3. The credit base.
        expected_base = np.maximum(ira + employer_plan + counted - distributions, 0)
        np.testing.assert_allclose(base, expected_base, atol=TOLERANCE, err_msg=message)
        whole_line_16_base = np.maximum(
            ira + employer_plan + line_16 - distributions, 0
        )
        assert np.all(base <= whole_line_16_base + TOLERANCE), message
        assert np.all(whole_line_16_base - base <= line_16 - counted + TOLERANCE), (
            message
        )
        # 4. The credit.
        assert np.all(credit >= -TOLERANCE), message
        assert np.all(
            credit <= TOP_RATE * np.minimum(base, CONTRIBUTION_CAP) + TOLERANCE
        ), message


profits = st.one_of(
    st.sampled_from([0, 1_000, 20_000, 100_000, 400_000]),
    st.integers(-20_000, 500_000),
)
deferrals = st.one_of(
    st.just(0),
    st.sampled_from([20_500, 23_500, 24_500, 31_000, 34_750]),
    st.integers(0, 40_000),
)
person_strategy = st.fixed_dictionaries(
    {
        "age": st.sampled_from([30, 49, 50, 55, 59, 60, 61, 63, 64, 70]),
        "employment_income": st.one_of(st.just(0), st.integers(0, 200_000)),
        "self_employment_income": profits,
        "self_employed_pension_contributions_desired": st.one_of(
            st.sampled_from([0, 1_000, 1_000_000]), st.integers(0, 100_000)
        ),
        "traditional_401k_contributions_desired": deferrals,
        "roth_401k_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 25_000)
        ),
        "traditional_403b_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 25_000)
        ),
        "roth_403b_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 25_000)
        ),
        "ira_compensation": st.one_of(st.just(0), st.integers(0, 20_000)),
        "traditional_ira_contributions_desired": st.one_of(
            st.just(0), st.integers(0, 8_000)
        ),
        "roth_ira_contributions_desired": st.one_of(st.just(0), st.integers(0, 8_000)),
        "retirement_distributions": st.one_of(st.just(0), st.integers(0, 60_000)),
    }
)

SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(person_strategy, min_size=4, max_size=15))
def test_credit_counts_only_the_elective_deferral_room(people_inputs):
    sim = Simulation(situation=build_situation(people_inputs))
    check(sim, people_inputs)


GRID_EMPLOYER_PLAN = [0, 10_000, 20_000, 23_500, 40_000]
GRID_LINE_16 = [0, 1_000, 5_000, 20_000, 60_000]


@pytest.fixture(scope="module")
def grid():
    people_inputs = [
        {
            "age": 55,
            "employment_income": 80_000,
            "self_employment_income": 300_000,
            "traditional_401k_contributions_desired": employer_plan,
            "self_employed_pension_contributions_desired": line_16,
        }
        for employer_plan, line_16 in itertools.product(
            GRID_EMPLOYER_PLAN, GRID_LINE_16
        )
    ]
    sim = Simulation(situation=build_situation(people_inputs))
    return sim, people_inputs


@pytest.mark.parametrize("year", YEARS)
def test_grid_is_monotone(grid, year):
    sim, people_inputs = grid
    check(sim, people_inputs)
    shape = len(GRID_EMPLOYER_PLAN), len(GRID_LINE_16)
    counted = sim.calculate("self_employed_pension_elective_deferrals", year).reshape(
        shape
    )
    # The counted deferrals rise with the line 16 contribution...
    assert np.all(np.diff(counted, axis=1) >= -TOLERANCE)
    # ...and fall as deferrals to an employer's plan use up the room.
    assert np.all(np.diff(counted, axis=0) <= TOLERANCE)
    # With deferrals of $40,000 to an employer's plan, no room is left.
    np.testing.assert_allclose(counted[-1], 0, atol=TOLERANCE)
