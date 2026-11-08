"""Invariants for the 2018-2026 histories of state employer unemployment taxes.

The tables below copy the new-employer rates and taxable wage bases that state
agencies published, from the sources cited in each parameter file, so these
tests compare the model with those publications and not with its own
parameters. Industry-average states (where new employers take the rate of their
industry) list the state's published average employer rate on taxable wages.

Two tests read the stored parameters without a simulation:

1. Schedule: in every month from 2015 through 2026, every jurisdiction's
   default rate and taxable wage base equal the published value for that
   month, and so do New Jersey's employer TDI and workforce fund rates, Rhode
   Island's Job Development Fund rate and 2019 adjustment, and Alaska's
   employee contribution rate. The model does not encode years before 2018, so
   2015-2017 read the 2018 value, an intended approximation that this test
   pins.
2. Dates: every stored value of a parameter that an annual rate averages
   begins a calendar quarter. The annual rates read only the four quarter
   starts, so this keeps them equal to the average of all twelve months.

Hypothesis draws batches of workers, each with wages, a raise and a state; a
seeded population puts two workers in every jurisdiction. Each batch runs as
one vectorized simulation covering SIMULATED_YEARS, which include the July-June
rate changes. For every worker and year:

3. Differential: each employer unemployment tax equals the published rate,
   averaged over the four quarter starts, times wages up to the published wage
   base; so do New Jersey's employer TDI and workforce fund contributions,
   Rhode Island's Job Development Fund tax and Alaska's employee contribution.
4. Bounds: each tax lies between zero and its highest quarterly rate times
   positive wages, and wages at or below zero owe nothing.
5. Monotonicity: no tax falls when wages rise.
6. Agreement: the employer-total paths equal the worker paths when the
   employer-total taxable wages equal the worker's.
7. Geography: outside its jurisdiction, each jurisdiction's tax is zero.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    STATE_UNEMPLOYMENT_TAX_JURISDICTIONS,
)

TOLERANCE = 0.01  # dollars
FIRST_YEAR = 2015  # policyengine_us.tools.parameters.FIRST_MODELED_YEAR
FIRST_PUBLISHED_YEAR = 2018
LAST_YEAR = 2026
MONTHS = range(1, 13)
QUARTER_START_MONTHS = (1, 4, 7, 10)

# Published new-employer rate and taxable wage base for each jurisdiction and
# year. A rate is one number, or four numbers when the rate changes inside the
# calendar year: the rates in force at the starts of the four quarters.
# BEGIN PUBLISHED_SUTA (generated from the curated source table)
PUBLISHED_SUTA = {
    "AK": {
        2018: (0.01, 39_500),
        2019: (0.01, 39_900),
        2020: (0.01, 41_500),
        2021: (0.0141, 43_600),
        2022: (0.0153, 45_200),
        2023: (0.0104, 47_100),
        2024: (0.01, 49_700),
        2025: (0.01, 51_700),
        2026: (0.01, 54_200),
    },
    "CT": {
        2018: (0.036, 15_000),
        2019: (0.034, 15_000),
        2020: (0.032, 15_000),
        2021: (0.03, 15_000),
        2022: (0.03, 15_000),
        2023: (0.028, 15_000),
        2024: (0.025, 25_000),
        2025: (0.022, 26_100),
        2026: (0.019, 27_000),
    },
    "IL": {
        2018: (0.03225, 12_960),
        2019: (0.03175, 12_960),
        2020: (0.03125, 12_740),
        2021: (0.03175, 12_960),
        2022: (0.03525, 12_960),
        2023: (0.0395, 13_271),
        2024: (0.0395, 13_590),
        2025: (0.0365, 13_916),
        2026: (0.0335, 14_250),
    },
    "NJ": {
        2018: (0.026825, 33_700),
        2019: (0.026825, 34_400),
        2020: (0.026825, 35_300),
        2021: (0.026825, 36_200),
        2022: ((0.026825, 0.026825, 0.029825, 0.029825), 39_800),
        2023: ((0.029825, 0.029825, 0.032825, 0.032825), 41_100),
        2024: ((0.032825, 0.032825, 0.029825, 0.029825), 42_300),
        2025: ((0.029825, 0.029825, 0.026825, 0.026825), 43_300),
        2026: (0.026825, 44_800),
    },
    "RI": {
        2018: (0.015, 23_000),
        2019: (0.0117, 23_600),
        2020: (0.0106, 24_000),
        2021: (0.0095, 24_600),
        2022: (0.0098, 24_600),
        2023: (0.0088, 28_200),
        2024: (0.0079, 29_200),
        2025: (0.01, 29_800),
        2026: (0.01, 30_800),
    },
}
# END PUBLISHED_SUTA

# New Jersey Department of Labor and Workforce Development, rate information:
# new-employer TDI rate and workforce development and supplemental workforce
# fund rate, both on the UI taxable wage base.
NJ_EMPLOYER_TDI_RATE = 0.005
NJ_EMPLOYER_WORKFORCE_RATE = 0.001175

# Rhode Island Job Development Fund assessment of 0.21%, with the 0.08%
# adjustment that applied for 2019 only (R.I. Gen. Laws 28-43-8.5; DLT 2019
# rates; Division of Taxation ADV 2019-37).
RI_JDF_RATE = {2019: 0.0029}
RI_JDF_DEFAULT_RATE = 0.0021

# Alaska employee unemployment insurance contribution rate (AS 23.20.290(d);
# DOLWD actuarial report Table 1.3 and new-employer rate notices).
AK_EMPLOYEE_RATE = {2022: 0.0056, 2023: 0.0051}
AK_EMPLOYEE_DEFAULT_RATE = 0.005

SIMULATED_YEARS = (2018, 2022, 2026)

CODES = [code for _, code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS]
GROUP = {code: group for group, code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS}
SLUG = {code: slug for _, code, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS}
P = system.parameters.gov


def _unemployment(code):
    return getattr(getattr(P, GROUP[code]), SLUG[code]).tax.payroll.unemployment


def _published(code, year):
    return PUBLISHED_SUTA[code][max(year, FIRST_PUBLISHED_YEAR)]


def _quarterly_rates(code, year):
    rate, _ = _published(code, year)
    return rate if isinstance(rate, tuple) else (rate,) * 4


def _annual_rate(code, year):
    return float(np.mean(_quarterly_rates(code, year)))


def _rate_in_month(code, year, month):
    return _quarterly_rates(code, year)[(month - 1) // 3]


def _wage_base(code, year):
    return _published(code, year)[1]


def _instants():
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for month in MONTHS:
            yield year, month, f"{year}-{month:02d}-01"


def test_every_jurisdiction_has_a_published_history():
    assert sorted(PUBLISHED_SUTA) == sorted(CODES)
    for code, table in PUBLISHED_SUTA.items():
        assert sorted(table) == list(range(FIRST_PUBLISHED_YEAR, LAST_YEAR + 1)), code


def test_stored_histories_match_published_tables_in_every_month():
    nj = P.states.nj.tax.payroll
    ri = P.states.ri.tax.payroll.job_development_fund
    ak = P.states.ak.tax.payroll.unemployment
    for year, month, instant in _instants():
        for code in CODES:
            parameters = _unemployment(code)
            assert parameters.default_rate(instant) == _rate_in_month(
                code, year, month
            ), (code, instant)
            assert parameters.taxable_wage_base(instant) == _wage_base(code, year), (
                code,
                instant,
            )
        assert nj.temporary_disability_insurance.employer_rate(instant) == (
            NJ_EMPLOYER_TDI_RATE
        )
        assert nj.workforce_development.employer_rate(instant) == (
            NJ_EMPLOYER_WORKFORCE_RATE
        )
        assert ri.employer_rate(instant) + ri.adjustment_rate(instant) == (
            RI_JDF_RATE.get(year, RI_JDF_DEFAULT_RATE)
        ), instant
        assert ak.employee_rate(instant) == AK_EMPLOYEE_RATE.get(
            year, AK_EMPLOYEE_DEFAULT_RATE
        ), instant


def test_quarter_averaged_parameters_change_only_at_quarter_starts():
    # A value dated inside a quarter would need the annual rate to read more
    # than the four quarter starts.
    nj = P.states.nj.tax.payroll
    averaged = [_unemployment(code).default_rate for code in CODES] + [
        nj.temporary_disability_insurance.employer_rate,
        nj.workforce_development.employer_rate,
    ]
    for parameter in averaged:
        for entry in parameter.values_list:
            _, month, day = entry.instant_str.split("-")
            assert int(month) in QUARTER_START_MONTHS and day == "01", (
                parameter.name,
                entry.instant_str,
            )


wages = st.one_of(
    st.integers(-50_000, 0).map(float),
    st.integers(0, 150_000).map(float),
)
workers = st.fixed_dictionaries(
    {
        "wages": wages,
        "raise": st.integers(0, 100_000).map(float),
        "state": st.sampled_from(CODES),
    }
)

SEED = 20261108


def _seeded_workers(per_jurisdiction=2):
    rng = np.random.default_rng(SEED)
    return [
        {
            "wages": float(rng.integers(-50_000, 150_001)),
            "raise": float(rng.integers(0, 100_001)),
            "state": code,
        }
        for code in CODES
        for _ in range(per_jurisdiction)
    ]


def _people(batch):
    # Each worker appears twice, at their wages and after their raise.
    return [
        {**worker, "wages": wages, "twin": i}
        for i, worker in enumerate(batch)
        for wages in (worker["wages"], worker["wages"] + worker["raise"])
    ]


def _situation(people):
    situation = {"people": {}, "households": {}}
    for i, person in enumerate(people):
        positive = max(person["wages"], 0)
        situation["people"][f"person_{i}"] = {
            "employment_income": {year: person["wages"] for year in SIMULATED_YEARS},
            "employer_total_taxable_earnings_for_state_unemployment_tax": {
                year: min(positive, _wage_base(person["state"], year))
                for year in SIMULATED_YEARS
            },
        }
        situation["households"][f"household_{i}"] = {
            "members": [f"person_{i}"],
            "state_code": {year: person["state"] for year in SIMULATED_YEARS},
        }
    return situation


def _calculate(sim, variable, year):
    return np.asarray(sim.calculate(variable, year), dtype=float)


def _check(batch):
    people = _people(batch)
    wages = np.array([person["wages"] for person in people])
    state = np.array([person["state"] for person in people])
    positive = np.maximum(wages, 0)
    base, raised = np.arange(0, len(people), 2), np.arange(1, len(people), 2)

    sim = Simulation(situation=_situation(people))
    for year in SIMULATED_YEARS:
        wage_base = np.array([_wage_base(code, year) for code in state])
        taxable = np.minimum(positive, wage_base)
        annual_rate = np.array([_annual_rate(code, year) for code in state])
        top_rate = np.array([max(_quarterly_rates(code, year)) for code in state])

        total = _calculate(sim, "employer_state_unemployment_tax", year)
        expected = {
            "employer_state_unemployment_tax": annual_rate * taxable,
            "nj_employer_temporary_disability_insurance_contribution": np.where(
                state == "NJ", NJ_EMPLOYER_TDI_RATE * taxable, 0
            ),
            "nj_employer_workforce_fund_contribution": np.where(
                state == "NJ", NJ_EMPLOYER_WORKFORCE_RATE * taxable, 0
            ),
            "ri_employer_job_development_fund_tax": np.where(
                state == "RI",
                RI_JDF_RATE.get(year, RI_JDF_DEFAULT_RATE) * taxable,
                0,
            ),
            "ak_employee_unemployment_insurance_contribution": np.where(
                state == "AK",
                AK_EMPLOYEE_RATE.get(year, AK_EMPLOYEE_DEFAULT_RATE) * taxable,
                0,
            ),
        }
        for variable, amount in expected.items():
            computed = (
                total
                if variable == "employer_state_unemployment_tax"
                else (_calculate(sim, variable, year))
            )
            # 3. Differential against the published tables; 7. geography for
            # the state-specific contributions, which are zero elsewhere.
            np.testing.assert_allclose(
                computed, amount, atol=TOLERANCE, rtol=0, err_msg=f"{variable} {year}"
            )
            # 4. Bounds.
            assert (computed >= 0).all(), (variable, year)
            np.testing.assert_array_equal(computed[wages <= 0], 0)
            # 5. Monotonicity.
            assert (computed[raised] >= computed[base] - TOLERANCE).all(), (
                variable,
                year,
            )
        assert (total <= top_rate * positive + TOLERANCE).all(), year

        # 7. Geography: each jurisdiction's tax is zero outside it, and the
        # jurisdiction taxes add up to the total.
        by_jurisdiction = 0
        for code in CODES:
            amount = _calculate(
                sim, f"{SLUG[code]}_employer_state_unemployment_tax", year
            )
            np.testing.assert_array_equal(amount[state != code], 0)
            by_jurisdiction = by_jurisdiction + amount
        np.testing.assert_allclose(by_jurisdiction, total, atol=TOLERANCE, rtol=0)

        # 6. Agreement of the employer-total and worker paths.
        np.testing.assert_allclose(
            _calculate(sim, "employer_total_state_unemployment_tax", year),
            total,
            atol=TOLERANCE,
            rtol=0,
            err_msg=f"employer_total_state_unemployment_tax {year}",
        )
        additional = _calculate(sim, "employer_additional_state_payroll_tax", year)
        total_additional = _calculate(
            sim, "employer_total_additional_state_payroll_tax", year
        )
        for code in ("NJ", "RI"):
            in_state = state == code
            np.testing.assert_allclose(
                total_additional[in_state],
                additional[in_state],
                atol=TOLERANCE,
                rtol=0,
                err_msg=f"employer_total_additional_state_payroll_tax {code} {year}",
            )


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(workers, min_size=1, max_size=12))
def test_employer_state_unemployment_tax_history_invariants(batch):
    _check(batch)


def test_employer_state_unemployment_tax_history_invariants_seeded_population():
    _check(_seeded_workers())
