"""Invariants for Hawaii's employee temporary disability insurance contribution.

YAML covers the policy examples. This module covers what one YAML case cannot
state:

1. Code against published figures. The wage base parameter follows HRS
   392-43(b)(2) from each DLIR notice's average annual wage, rounded to $100 as
   HRS 383-61(b) computes it; each notice's own base follows from the same
   average before rounding; each notice's maximum weekly deduction is 0.5% of
   its base; and the two bases stay within the gap that rounding can open.
2. The annual formula against the weekly statute. The law caps wages week by
   week. For any wages spread over a worker's weeks, the annual amount is at
   least the weekly sum, and the two match when wages are even.
3. Properties across drawn batches of workers: bounds, monotonicity in wages,
   state masking, and aggregation to the tax unit.
4. Qualification. Previous-year history can only add workers, and exactly the
   workers whose history clears the wages, weeks and hours minimums, when the
   simulation year's pay, excluded payments, weeks and hours are on file.
   Before the first modeled year the history comes from inputs alone,
   whatever the simulation calculated first.
5. Net income. Removing the contribution raises household net income by exactly
   the contribution.

Intended differences from the published figures:

- HRS 392-43(b)(2) takes the average annual wage as HRS 383-61(b) determines
  it, and 383-61(b) computes that average rounded to the nearest hundred
  dollars. DLIR's notices use the average before rounding, so the parameter
  runs from 0.84 below to 1.15 above the published base
  (us-hi:tdi-wage-base-rounded-average in source_conflicts/candidates.yaml).
- The parameter rounds the base once, to the cent. The 2010 notice does the
  same; every other notice rounds the weekly wage to the cent first, which
  would move 14 of the 23 parameter values by a cent.
- A full-year worker over the cap pays 52 * 0.5% * base here. DLIR rounds each
  week's maximum deduction to the cent, so 52 weeks of it differ by at most 26
  cents.
"""

from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

CONTRIBUTION = "hi_employee_temporary_disability_insurance_contribution"
QUALIFIED = "hi_temporary_disability_insurance_qualified"
TOLERANCE = 0.01  # dollars
RATE = Decimal("0.005")  # HRS 392-43(a)
FACTOR = Decimal("1.21")  # HRS 392-43(b)(2)

# Transcribed from each year's DLIR notice, independent of the parameter file:
# state average annual wage, maximum weekly wage base, maximum weekly deduction.
NOTICES = {
    2004: ("30972.13", "720.70", "3.60"),
    2005: ("32336.24", "752.44", "3.76"),
    2006: ("34023.65", "791.70", "3.96"),
    2007: ("35250.68", "820.26", "4.10"),
    2008: ("36209.17", "842.56", "4.21"),
    2009: ("37718.93", "877.69", "4.39"),
    2010: ("38750.59", "901.70", "4.51"),
    2011: ("38002.62", "884.29", "4.42"),
    2012: ("38818.32", "903.28", "4.52"),
    2013: ("39613.57", "921.78", "4.61"),
    2014: ("40398.56", "940.05", "4.70"),
    2015: ("40879.44", "951.23", "4.76"),
    2016: ("42217.41", "982.36", "4.91"),
    2017: ("43976.82", "1023.31", "5.12"),
    2018: ("45924.45", "1068.62", "5.34"),
    2019: ("46760.69", "1088.08", "5.44"),
    2020: ("48108.20", "1119.44", "5.60"),
    2021: ("47397.51", "1102.90", "5.51"),
    2022: ("51582.77", "1200.30", "6.00"),
    2023: ("56662.05", "1318.48", "6.59"),
    2024: ("59081.47", "1374.78", "6.87"),
    2025: ("61958.21", "1441.72", "7.21"),
    2026: ("64471.82", "1500.21", "7.50"),
}
YEARS = sorted(NOTICES)
# HRS 383-11(1)(A) and (4)(A).
DEFERRALS = (
    "traditional_401k_contributions",
    "roth_401k_contributions",
    "traditional_403b_contributions",
    "roth_403b_contributions",
)
GROUP_ENTITIES = (
    "tax_units",
    "spm_units",
    "families",
    "marital_units",
    "households",
)
TDI = SYSTEM.parameters.gov.states.hi.tax.payroll.temporary_disability_insurance

# A batch's cost is mostly per-variable overhead, so each example is a batch of
# workers and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def cents(amount):
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def statutory_base(year):
    # HRS 383-61(b) rounds the average to the nearest hundred dollars, and HRS
    # 392-43(b)(2) takes one fifty-second of it times 1.21.
    average = Decimal(NOTICES[year][0])
    hundreds = (average / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100
    return cents(hundreds * FACTOR / 52)


def base_for(year):
    return float(statutory_base(year))


def simulate(year, workers, **overrides):
    period = str(year)
    previous = str(year - 1)
    situation = {"people": {}, **{entity: {} for entity in GROUP_ENTITIES}}
    for i, worker in enumerate(workers):
        person = f"person_{i}"
        situation["people"][person] = {
            "age": {period: 40},
            "employment_income": {
                previous: worker.get("previous_wages", 0),
                period: worker["wages"],
            },
            "pre_tax_health_insurance_premiums": {period: worker.get("premiums", 0)},
            "military_basic_pay": {period: worker.get("military", 0)},
            "dependent_care_employer_benefits": {
                period: worker.get("dependent_care", 0)
            },
            **{
                kind: {
                    period: worker.get("deferral", 0)
                    if kind == worker.get("deferral_kind")
                    else 0
                }
                for kind in DEFERRALS
            },
            "weeks_worked": {
                previous: worker.get("previous_weeks", 0),
                period: worker.get("weeks", 0),
            },
            "weekly_hours_worked_before_lsr": {
                previous: worker.get("previous_hours", 0),
                period: worker.get("hours", 0),
            },
            **{name: {period: value} for name, value in overrides.items()},
        }
        for entity in GROUP_ENTITIES:
            situation[entity][f"{entity}_{i}"] = {"members": [person]}
        situation["households"][f"households_{i}"]["state_code"] = {
            period: worker.get("state", "HI")
        }
    return Simulation(tax_benefit_system=SYSTEM, situation=situation)


@pytest.mark.parametrize("year", YEARS)
def test_parameters_follow_the_statute_from_each_notice_average(year):
    instant = f"{year}-01-01"
    assert TDI.maximum_weekly_wage_base(instant) == pytest.approx(
        base_for(year), abs=1e-9
    )
    assert TDI.employee_rate(instant) == float(RATE)


@pytest.mark.parametrize("year", YEARS)
def test_notice_applies_the_formula_to_the_average_before_rounding(year):
    annual_wage, base, deduction = (Decimal(value) for value in NOTICES[year])
    rounded_once = cents(annual_wage / 52 * FACTOR)
    weekly_wage_rounded_first = cents(cents(annual_wage / 52) * FACTOR)
    assert base == (rounded_once if year == 2010 else weekly_wage_rounded_first)
    assert deduction == cents(base * RATE)
    assert abs(52 * base * RATE - 52 * deduction) <= Decimal("0.26")
    # Rounding moves the average by at most 50, so the bases differ by at most
    # 50 * 1.21 / 52 = 1.1635, plus up to 0.016 of rounding to cents.
    assert abs(statutory_base(year) - base) <= Decimal("1.18")


workers = st.fixed_dictionaries(
    {
        "state": st.sampled_from(["HI", "HI", "HI", "TX"]),
        "wages": st.one_of(
            st.sampled_from([0, 399, 400, 1_000_000]),
            st.integers(-5_000, 200_000),
        ),
        "premiums": st.one_of(st.just(0), st.integers(0, 10_000)),
        "military": st.one_of(st.just(0), st.integers(0, 10_000)),
        "deferral": st.one_of(st.just(0), st.integers(0, 10_000)),
        "deferral_kind": st.sampled_from(DEFERRALS),
        "dependent_care": st.one_of(st.just(0), st.integers(0, 5_000)),
        "weeks": st.one_of(st.sampled_from([0, 13, 14, 52]), st.integers(1, 52)),
        "hours": st.one_of(st.sampled_from([0, 19, 20, 40]), st.integers(1, 80)),
    }
)


@settings(**SETTINGS)
@given(
    year=st.sampled_from(YEARS),
    batch=st.lists(workers, min_size=5, max_size=30),
    bump=st.integers(1, 20_000),
)
def test_contribution_properties(year, batch, bump):
    period = str(year)
    sim = simulate(year, batch)
    contribution = sim.calculate(CONTRIBUTION, period)
    raised = simulate(
        year, [{**worker, "wages": worker["wages"] + bump} for worker in batch]
    ).calculate(CONTRIBUTION, period)

    in_hawaii = np.array([worker["state"] == "HI" for worker in batch])
    wages = np.array(
        [
            max(
                0,
                worker["wages"]
                - worker["premiums"]
                - worker["military"]
                - worker["deferral"],
            )
            for worker in batch
        ],
        dtype=float,
    )
    weeks = np.array([worker["weeks"] or 52 for worker in batch], dtype=float)
    limit = float(RATE) * np.minimum(wages, base_for(year) * weeks)

    # Bounds, for every input.
    assert (contribution >= 0).all()
    assert (contribution <= limit + TOLERANCE).all()
    # State masking.
    assert (contribution[~in_hawaii] == 0).all()
    # More wages never lower the contribution.
    assert (raised >= contribution - TOLERANCE).all()
    # Each worker files alone, so the tax unit total is that worker's amount.
    assert sim.calculate("hi_employee_state_payroll_tax", period) == pytest.approx(
        contribution, abs=TOLERANCE
    )
    assert sim.calculate("employee_state_payroll_tax", period)[
        in_hawaii
    ] == pytest.approx(contribution[in_hawaii], abs=TOLERANCE)


@settings(**SETTINGS)
@given(
    year=st.sampled_from(YEARS),
    batch=st.lists(
        st.tuples(
            workers,
            st.sampled_from([0, 399, 400, 10_000]),
            st.sampled_from([0, 13, 14, 52]),
            st.sampled_from([0, 19, 20, 40]),
        ),
        min_size=5,
        max_size=30,
    ),
)
def test_previous_year_history_only_adds_workers_who_clear_it(year, batch):
    # simulate() enters the simulation year's weeks and hours, zero included,
    # so no history carries into that year.
    period = str(year)
    alone = simulate(year, [worker for worker, _, _, _ in batch]).calculate(
        QUALIFIED, period
    )
    with_history = simulate(
        year,
        [
            {
                **worker,
                "previous_wages": wages,
                "previous_weeks": weeks,
                "previous_hours": hours,
            }
            for worker, wages, weeks, hours in batch
        ],
    ).calculate(QUALIFIED, period)

    in_hawaii = np.array([worker["state"] == "HI" for worker, _, _, _ in batch])
    clears = np.array(
        [
            wages >= 400 and weeks >= 14 and hours >= 20
            for _, wages, weeks, hours in batch
        ]
    )
    assert (with_history[in_hawaii] == (alone | clears)[in_hawaii]).all()
    assert not with_history[~in_hawaii].any()


def test_history_before_the_first_modeled_year_is_read_not_calculated():
    # A short 2015 passes on 2014 history provided as inputs, and 2014 keeps
    # only those inputs: the model calculates and caches nothing before 2015.
    year = FIRST_MODELED_YEAR
    sim = simulate(
        year,
        [
            {
                "wages": 900,
                "weeks": 1,
                "hours": 40,
                "previous_wages": 52_000,
                "previous_weeks": 52,
                "previous_hours": 40,
                "state": "HI",
            }
        ],
    )
    assert sim.calculate(QUALIFIED, str(year)).tolist() == [True]
    early = {
        name
        for population in sim.populations.values()
        for name, holder in population._holders.items()
        for known in holder.get_known_periods()
        if known.unit != "eternity" and known.start.year < FIRST_MODELED_YEAR
    }
    assert early == {
        "employment_income_before_lsr",
        "weeks_worked",
        "weekly_hours_worked_before_lsr",
    }


def test_history_before_the_first_modeled_year_ignores_calculated_values():
    # Before 2015 the previous year counts inputs only. Calculating the 2014
    # 401(k) contribution from a desired deferral first must not let that
    # deferral reach the 2015 test: 10,000 of 2014 pay passes in either order.
    year = FIRST_MODELED_YEAR
    previous = str(year - 1)
    worker = {
        "wages": 900,
        "weeks": 1,
        "hours": 40,
        "previous_wages": 10_000,
        "previous_weeks": 52,
        "previous_hours": 40,
        "state": "HI",
    }
    results = []
    for calculate_deferral_first in (False, True):
        sim = simulate(year, [worker])
        sim.set_input(
            "traditional_401k_contributions_desired", previous, np.array([9_700.0])
        )
        if calculate_deferral_first:
            deferral = sim.calculate("traditional_401k_contributions", previous)
            assert deferral.tolist() == pytest.approx([9_700])
        results.append(
            (
                sim.calculate(QUALIFIED, str(year)).tolist(),
                sim.calculate(CONTRIBUTION, str(year)).tolist(),
            )
        )
    # 900 falls under the 951.71 cap for one week: 0.5% * 900 = 4.50.
    for qualified, contribution in results:
        assert qualified == [True]
        assert contribution == pytest.approx([4.50], abs=TOLERANCE)


# At least 14 weeks of at least 30 dollars clears the $400 and 14-week test.
weekly_wages = st.lists(st.integers(30, 4_000), min_size=14, max_size=52)


@settings(**SETTINGS)
@given(
    year=st.sampled_from(YEARS),
    batch=st.lists(weekly_wages, min_size=3, max_size=15),
)
def test_annual_amount_is_the_limit_of_the_weekly_statute(year, batch):
    base = base_for(year)
    annual = simulate(
        year,
        [{"wages": sum(series), "weeks": len(series), "hours": 40} for series in batch],
    ).calculate(CONTRIBUTION, str(year))

    statute = np.array(
        [sum(float(RATE) * min(wage, base) for wage in series) for series in batch]
    )
    assert (annual >= statute - TOLERANCE).all()

    even = np.array(
        [
            len(series) * float(RATE) * min(sum(series) / len(series), base)
            for series in batch
        ]
    )
    assert annual == pytest.approx(even, abs=TOLERANCE)


def test_contribution_lowers_household_net_income_dollar_for_dollar():
    period = "2026"
    batch = [{"wages": wages} for wages in (30_000, 60_000, 100_000)]
    baseline = simulate(2026, batch)
    without = simulate(2026, batch, **{CONTRIBUTION: 0})

    contribution = baseline.calculate(CONTRIBUTION, period)
    # 0.5% of 30,000 and 60,000, then 0.5% * 52 * 1,500.87.
    assert contribution == pytest.approx([150, 300, 390.2262], abs=TOLERANCE)

    for variable in (
        "employee_state_payroll_tax",
        "employee_payroll_tax",
        "household_tax_before_refundable_credits",
    ):
        added = baseline.calculate(variable, period) - without.calculate(
            variable, period
        )
        assert added == pytest.approx(contribution, abs=TOLERANCE), variable

    lost = without.calculate("household_net_income", period) - baseline.calculate(
        "household_net_income", period
    )
    assert lost == pytest.approx(contribution, abs=TOLERANCE)
