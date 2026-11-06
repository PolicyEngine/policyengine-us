"""Invariants for the District of Columbia Paid Family Leave employer tax.

The Department of Employment Services (DOES) publishes the tax rate for each
calendar quarter under "Historical PFL Tax Rate Information" at
https://dcpaidfamilyleave.dc.gov/employer-information/. DOES_QUARTERLY_RATES
copies that table, so these tests compare the model with the published rates
and not with its own parameters.

Two tests read the stored parameter without a simulation:

1. Schedule: in every month from 2015 through 2026, the stored rate equals the
   DOES rate for that month's quarter, and zero before 2019 Q2.
2. Dates: every stored rate begins a calendar quarter. The annual rate reads
   only the four quarter starts, so this keeps it equal to the average of all
   twelve months.

Hypothesis draws batches of workers, each with annual wages and a state; a
seeded population of 100 workers adds breadth. Each batch runs as one vectorized
simulation covering SIMULATED_YEARS. For every worker and year:

3. Differential: in DC, the annual rate equals the mean of the DOES quarterly
   rates, and the tax equals the sum over quarters of the DOES rate times a
   quarter of the worker's positive wages. In a year with one rate throughout,
   the annual rate equals the stored rate on January 1.
4. Bounds: in DC, the annual rate lies between the year's lowest and highest
   quarterly rates, and the tax lies between zero and the top rate times
   positive wages.
5. Monotonicity: in DC, the tax never falls as wages rise, with no wage cap, and
   wages at or below zero owe no tax.
6. Agreement: the employer-total path equals the worker path when its taxable
   wages equal the worker's positive wages.
7. Geography: outside DC, the rate and both tax paths are zero in every year.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

TOLERANCE = 0.01  # dollars
RATE_TOLERANCE = 1e-8

# DOES, "Historical PFL Tax Rate Information". The table starts with 2019
# Quarter 2 and ends with 2026 Quarter 4.
DOES_QUARTERLY_RATES = {
    2019: (0, 0.0062, 0.0062, 0.0062),
    2020: (0.0062, 0.0062, 0.0062, 0.0062),
    2021: (0.0062, 0.0062, 0.0062, 0.0062),
    2022: (0.0062, 0.0062, 0.0026, 0.0026),
    2023: (0.0026, 0.0026, 0.0026, 0.0026),
    2024: (0.0026, 0.0026, 0.0075, 0.0075),
    2025: (0.0075, 0.0075, 0.0075, 0.0075),
    2026: (0.0075, 0.0075, 0.0075, 0.0075),
}
NO_RATE = (0, 0, 0, 0)
TOP_RATE = 0.0075

# Each new year adds four parameter-tree snapshots to the process, so simulate
# one year per case: before the tax, its first year, each steady rate and each
# change. The schedule test covers every month of the other years.
SIMULATED_YEARS = (2018, 2019, 2021, 2022, 2023, 2024, 2025)

RATE_SCHEDULE = system.parameters.gov.states.dc.tax.payroll.paid_leave.employer_rate

STATES = ["DC", "MD", "VA"]
wages = st.one_of(
    st.integers(-50_000, 0).map(float),
    st.integers(0, 2_000_000).map(float),
)
workers = st.fixed_dictionaries({"wages": wages, "state": st.sampled_from(STATES)})

SEED = 20261106


def _seeded_workers(n=100):
    rng = np.random.default_rng(SEED)
    return [
        {
            "wages": float(rng.integers(-50_000, 2_000_001)),
            "state": str(rng.choice(STATES)),
        }
        for _ in range(n)
    ]


def _situation(batch):
    # One simulation holds every year: each input is keyed by all the years.
    def every_year(value):
        return {year: value for year in SIMULATED_YEARS}

    people, households = {}, {}
    for i, worker in enumerate(batch):
        people[f"worker_{i}"] = {
            "employment_income": every_year(worker["wages"]),
            "employer_total_dc_paid_leave_taxable_wages": every_year(
                max(worker["wages"], 0)
            ),
        }
        households[f"household_{i}"] = {
            "members": [f"worker_{i}"],
            "state_code": every_year(worker["state"]),
        }
    return {"people": people, "households": households}


def _check(batch):
    wage_array = np.array([worker["wages"] for worker in batch])
    in_dc = np.array([worker["state"] == "DC" for worker in batch])
    positive_wages = np.maximum(wage_array, 0)
    # Sort DC workers by wages to compare neighbors for monotonicity.
    dc_order = np.argsort(wage_array[in_dc])

    sim = Simulation(situation=_situation(batch))
    for year in SIMULATED_YEARS:
        quarterly = DOES_QUARTERLY_RATES.get(year, NO_RATE)
        rate = np.asarray(
            sim.calculate("dc_employer_paid_leave_tax_rate", year), dtype=float
        )
        tax = np.asarray(sim.calculate("dc_employer_paid_leave_tax", year), dtype=float)
        employer_total = np.asarray(
            sim.calculate("employer_total_additional_state_payroll_tax", year),
            dtype=float,
        )

        # 3. Differential against the DOES table.
        np.testing.assert_allclose(
            rate[in_dc], np.mean(quarterly), atol=RATE_TOLERANCE, rtol=0
        )
        expected_tax = sum(
            quarter_rate * positive_wages[in_dc] / 4 for quarter_rate in quarterly
        )
        np.testing.assert_allclose(tax[in_dc], expected_tax, atol=TOLERANCE, rtol=0)
        if len(set(quarterly)) == 1:
            np.testing.assert_allclose(
                rate[in_dc],
                RATE_SCHEDULE(f"{year}-01-01"),
                atol=RATE_TOLERANCE,
                rtol=0,
            )

        # 4. Bounds.
        assert (rate[in_dc] >= min(quarterly) - RATE_TOLERANCE).all()
        assert (rate[in_dc] <= max(quarterly) + RATE_TOLERANCE).all()
        assert (tax[in_dc] >= 0).all()
        assert (tax[in_dc] <= TOP_RATE * positive_wages[in_dc] + TOLERANCE).all()

        # 5. Monotonicity, and no tax on wages at or below zero.
        assert (np.diff(tax[in_dc][dc_order]) >= -TOLERANCE).all()
        np.testing.assert_array_equal(tax[in_dc & (wage_array <= 0)], 0)

        # 6. Agreement of the two paths.
        np.testing.assert_allclose(employer_total, tax, atol=TOLERANCE, rtol=0)

        # 7. Geography.
        np.testing.assert_array_equal(rate[~in_dc], 0)
        np.testing.assert_array_equal(tax[~in_dc], 0)
        np.testing.assert_array_equal(employer_total[~in_dc], 0)


def test_stored_rate_matches_does_table_in_every_month():
    for year in range(2015, 2027):
        quarterly = DOES_QUARTERLY_RATES.get(year, NO_RATE)
        for month in range(1, 13):
            assert (
                RATE_SCHEDULE(f"{year}-{month:02d}-01") == quarterly[(month - 1) // 3]
            )


def test_every_stored_rate_begins_a_calendar_quarter():
    # A rate dated inside a quarter would need the annual rate to read more
    # than the four quarter starts.
    for entry in RATE_SCHEDULE.values_list:
        _, month, day = entry.instant_str.split("-")
        assert int(month) in (1, 4, 7, 10) and day == "01", entry.instant_str


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(workers, min_size=1, max_size=12))
def test_dc_paid_leave_employer_rate_invariants(batch):
    _check(batch)


def test_dc_paid_leave_employer_rate_invariants_seeded_population():
    _check(_seeded_workers())
