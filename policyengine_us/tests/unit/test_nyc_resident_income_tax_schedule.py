"""NYC resident income tax schedule: differential and invariant tests.

`nyc_income_tax_before_credits` applies one marginal rate scale per filing
status (parameters/gov/local/ny/nyc/tax/income/rates). Each scale combines two
taxes that New York law authorizes for the same taxable years:

- the rate schedule of Tax Law 1304(a)(1)-(3)(A) (NYC Admin Code 11-1701(a))
  for taxable years beginning before 2030, and the lower 1304(b) schedule
  (11-1701(b)) for taxable years beginning after 2029 (Tax Law 1301(a)(1));
- the 14% additional tax of Tax Law 1304-B(a)(1) (NYC Admin Code
  11-1704.1(a)(1)), which applies to taxable years beginning before 2030.

Chapter 127 of 2026 (A.11561, Part D) moved both sunsets from "before 2027" to
"before 2030":
https://legislation.nysenate.gov/pdf/bills/2025/A11561#page=5

Differential tests compare the parameters and the variable against
independent transcriptions of:

- the Tax Law 1304(a)(n)(A) and 1304(b)(n) tables, as in effect after
  chapter 127 of 2026 (https://www.nysenate.gov/legislation/laws/TAX/1304);
- the 2025 IT-201-I New York City tax rate schedule, which already includes
  the additional tax
  (https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=40).

The tables state each bracket's base tax in whole dollars, so the model, which
accumulates exact marginal amounts, may differ from them by up to half a
dollar (scaled by 1.14 where the additional tax applies).

Invariants:
- 2027, 2028 and 2029 tax equals 2026 tax at every city taxable income and
  filing status (the rates are extended and the brackets are not indexed).
- Tax equals 114% of the 1304(a)(n)(A) marginal tax through 2029, and exactly
  the 1304(b) marginal tax from 2030.
- From 2030, tax is strictly lower than in 2029 at every positive income.
- Tax is non-negative, zero at zero income, continuous, and never falls as
  income rises, with marginal rates equal to the statutory rates.
- Joint filers and surviving spouses share one schedule, as do single and
  separate filers (the statute groups them).
"""

import numpy as np
import pytest
from policyengine_core.taxscales import MarginalRateTaxScale

from policyengine_us import Simulation
from policyengine_us.system import system

STATUSES = ["SINGLE", "SEPARATE", "HEAD_OF_HOUSEHOLD", "JOINT", "SURVIVING_SPOUSE"]
PARAMETER_NAME = {
    "SINGLE": "single",
    "SEPARATE": "separate",
    "HEAD_OF_HOUSEHOLD": "head_of_household",
    "JOINT": "joint",
    "SURVIVING_SPOUSE": "surviving_spouse",
}
# Tax Law 1304(a)(1)-(3) and (b)(1)-(3): joint returns and surviving spouses,
# heads of households, and all other residents.
PARAGRAPH = {
    "SINGLE": 3,
    "SEPARATE": 3,
    "HEAD_OF_HOUSEHOLD": 2,
    "JOINT": 1,
    "SURVIVING_SPOUSE": 1,
}

# Each table row is (over, base tax, rate on the excess over `over`).
# Tax Law 1304(a)(n)(A), "for taxable years beginning after two thousand
# sixteen".
TAX_LAW_1304_A = {
    1: [
        (0, 0, 0.027),
        (21_600, 583, 0.033),
        (45_000, 1_355, 0.0335),
        (90_000, 2_863, 0.034),
    ],
    2: [
        (0, 0, 0.027),
        (14_400, 389, 0.033),
        (30_000, 904, 0.0335),
        (60_000, 1_909, 0.034),
    ],
    3: [
        (0, 0, 0.027),
        (12_000, 324, 0.033),
        (25_000, 753, 0.0335),
        (50_000, 1_591, 0.034),
    ],
}
# Tax Law 1304(b)(n), "for taxable years beginning after two thousand
# twenty-nine".
TAX_LAW_1304_B = {
    1: [
        (0, 0, 0.0118),
        (21_600, 255, 0.01435),
        (45_000, 591, 0.01455),
        (90_000, 1_245, 0.0148),
    ],
    2: [
        (0, 0, 0.0118),
        (14_400, 170, 0.01435),
        (30_000, 394, 0.01455),
        (60_000, 830, 0.0148),
    ],
    3: [
        (0, 0, 0.0118),
        (12_000, 142, 0.01435),
        (25_000, 328, 0.01455),
        (50_000, 692, 0.0148),
    ],
}
# 2025 IT-201-I, New York City tax rate schedule (page 40), which applies the
# 14% additional tax to the 1304(a)(n)(A) rates.
IT_201_I_2025 = {
    1: [
        (0, 0, 0.03078),
        (21_600, 665, 0.03762),
        (45_000, 1_545, 0.03819),
        (90_000, 3_264, 0.03876),
    ],
    2: [
        (0, 0, 0.03078),
        (14_400, 443, 0.03762),
        (30_000, 1_030, 0.03819),
        (60_000, 2_176, 0.03876),
    ],
    3: [
        (0, 0, 0.03078),
        (12_000, 369, 0.03762),
        (25_000, 858, 0.03819),
        (50_000, 1_813, 0.03876),
    ],
}
ADDITIONAL_TAX_RATE = 0.14  # Tax Law 1304-B(a)(1)(ii)
LAST_EXTENDED_YEAR = 2029  # Chapter 127 of 2026: "before two thousand thirty"

EXTENDED_YEARS = [2017, 2020, 2025, 2026, 2027, 2028, 2029]
BASE_RATE_YEARS = [2030, 2031, 2035, 2050]


def extended(year):
    return year <= LAST_EXTENDED_YEAR


def statutory_table(status, year):
    tables = TAX_LAW_1304_A if extended(year) else TAX_LAW_1304_B
    return tables[PARAGRAPH[status]]


def additional_tax_factor(year):
    return 1 + ADDITIONAL_TAX_RATE if extended(year) else 1


def table_tax(table, income):
    """Tax from a published table: base tax of the row plus rate on the excess."""
    income = np.asarray(income, dtype=float)
    tax = np.zeros_like(income)
    for over, base, rate in table:
        in_row = income > over
        tax = np.where(in_row, base + rate * (income - over), tax)
    return tax


def marginal_tax(table, income):
    """Tax from the table's rates and thresholds alone, ignoring its base tax."""
    scale = MarginalRateTaxScale()
    for over, _, rate in table:
        scale.add_bracket(over, rate)
    return scale.calc(np.asarray(income, dtype=float))


def rate_scale(status, year):
    rates = system.parameters(f"{year}-01-01").gov.local.ny.nyc.tax.income.rates
    return getattr(rates, PARAMETER_NAME[status])


def income_grid(status):
    thresholds = [over for over, _, _ in TAX_LAW_1304_A[PARAGRAPH[status]]]
    near_thresholds = [t + d for t in thresholds for d in (-1, -0.01, 0, 0.01, 1)]
    spread = np.concatenate(
        [np.arange(0, 100_000, 2_500), np.geomspace(100_000, 5_000_000, 12)]
    )
    return np.unique(np.clip(np.concatenate([near_thresholds, spread]), 0, None))


@pytest.mark.parametrize("year", EXTENDED_YEARS + BASE_RATE_YEARS)
@pytest.mark.parametrize("status", STATUSES)
def test_rates_and_thresholds_match_the_statute(status, year):
    scale = rate_scale(status, year)
    table = statutory_table(status, year)
    factor = additional_tax_factor(year)
    np.testing.assert_array_equal(scale.thresholds, [over for over, _, _ in table])
    np.testing.assert_allclose(
        scale.rates, [rate * factor for _, _, rate in table], rtol=0, atol=1e-12
    )


@pytest.mark.parametrize("year", EXTENDED_YEARS + BASE_RATE_YEARS)
@pytest.mark.parametrize("status", STATUSES)
def test_tax_matches_the_statutory_table(status, year):
    income = income_grid(status)
    table = statutory_table(status, year)
    factor = additional_tax_factor(year)
    model = rate_scale(status, year).calc(income)
    # The model is the table's marginal tax (plus the additional tax) exactly,
    # and the table's whole-dollar base taxes are within half a dollar of it.
    np.testing.assert_allclose(
        model, factor * marginal_tax(table, income), rtol=1e-12, atol=1e-9
    )
    discrepancy = np.abs(model - factor * table_tax(table, income))
    assert discrepancy.max() <= 0.5 * factor + 1e-9


@pytest.mark.parametrize("status", STATUSES)
def test_2025_tax_matches_the_published_it_201_schedule(status):
    income = income_grid(status)
    published = table_tax(IT_201_I_2025[PARAGRAPH[status]], income)
    model = rate_scale(status, 2025).calc(income)
    assert np.abs(model - published).max() <= 0.5 + 1e-9


@pytest.mark.parametrize("year", EXTENDED_YEARS + BASE_RATE_YEARS)
def test_statute_groups_filing_statuses(year):
    income = income_grid("JOINT")
    for a, b in [("JOINT", "SURVIVING_SPOUSE"), ("SINGLE", "SEPARATE")]:
        np.testing.assert_array_equal(
            rate_scale(a, year).calc(income), rate_scale(b, year).calc(income)
        )


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("year", range(2017, 2036))
def test_schedule_is_continuous_and_nondecreasing(year, seed):
    rng = np.random.default_rng(seed)
    for status in STATUSES:
        scale = rate_scale(status, year)
        income = np.sort(
            np.concatenate(
                [
                    rng.uniform(0, 150_000, 200),
                    rng.lognormal(12, 1.5, 200),
                    scale.thresholds,
                ]
            )
        )
        tax = scale.calc(income)
        assert scale.calc(np.array([0.0]))[0] == 0
        assert (tax >= 0).all()
        assert (np.diff(tax) >= -1e-9).all()
        # No jump at a threshold: a cent more income adds at most a cent of
        # tax times the top rate.
        step = scale.calc(income + 0.01) - tax
        assert (step >= -1e-9).all() and (step <= 0.01 * max(scale.rates) + 1e-9).all()
        # Strictly inside each bracket, the marginal rate is that bracket's rate.
        bounds = list(scale.thresholds) + [scale.thresholds[-1] + 1_000_000]
        for low, high, rate in zip(bounds[:-1], bounds[1:], scale.rates):
            inside = rng.uniform(low + 1, high - 1, 20)
            slope = (scale.calc(inside + 1) - scale.calc(inside)) / 1
            np.testing.assert_allclose(slope, rate, rtol=0, atol=1e-9)


SIMULATION_YEARS = [2025, 2026, 2027, 2028, 2029, 2030, 2031]


@pytest.fixture(scope="module")
def grid_simulation():
    """One NYC tax unit per (filing status, city taxable income) grid point,
    with the same nominal city taxable income in every simulated year."""
    rows = [(status, income) for status in STATUSES for income in income_grid(status)]
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (status, income) in enumerate(rows):
        situation["people"][f"p{i}"] = {"age": {year: 40 for year in SIMULATION_YEARS}}
        situation["tax_units"][f"t{i}"] = {
            "members": [f"p{i}"],
            "filing_status": {year: status for year in SIMULATION_YEARS},
            "nyc_taxable_income": {year: float(income) for year in SIMULATION_YEARS},
        }
        situation["households"][f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {year: "NY" for year in SIMULATION_YEARS},
            "in_nyc": {year: True for year in SIMULATION_YEARS},
        }
    sim = Simulation(situation=situation)
    return {
        "status": np.array([status for status, _ in rows]),
        "income": np.array([income for _, income in rows], dtype=float),
        "tax": {
            year: sim.calculate("nyc_income_tax_before_credits", year)
            for year in SIMULATION_YEARS
        },
    }


@pytest.mark.parametrize("year", [2027, 2028, 2029])
def test_extended_years_tax_equals_2026_tax(grid_simulation, year):
    tax = grid_simulation["tax"]
    np.testing.assert_array_equal(tax[year], tax[2026])
    # Guard against a vacuous pass: the grid reaches every bracket.
    assert (tax[2026] > 0).any() and len(np.unique(tax[2026])) > 100


@pytest.mark.parametrize("year", SIMULATION_YEARS)
def test_variable_applies_the_statute_and_additional_tax(grid_simulation, year):
    g = grid_simulation
    for status in STATUSES:
        rows = g["status"] == status
        income = g["income"][rows]
        expected = additional_tax_factor(year) * marginal_tax(
            statutory_table(status, year), income
        )
        np.testing.assert_allclose(g["tax"][year][rows], expected, rtol=1e-6, atol=1e-2)


def test_tax_falls_when_the_extension_ends(grid_simulation):
    tax, income = grid_simulation["tax"], grid_simulation["income"]
    positive = income > 0
    assert (tax[2030][positive] < tax[LAST_EXTENDED_YEAR][positive]).all()
    np.testing.assert_array_equal(tax[2031], tax[2030])
