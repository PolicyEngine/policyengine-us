"""Arkansas's statutory CPI-U window, cap, floor, rounding and compounding.

A.C.A. 26-51-201(d)(2), as amended by Act 1459 of 2013, section 2, compares
the CPI for the current calendar year (the twelve months ending August 31)
with the preceding calendar year's. So tax year Y uses September Y-1 through
August Y over September Y-2 through August Y-1. The tiny trees below hold
only CPI-U and the Arkansas parameters, so the index cannot read chained
CPI-U or the IRS index. The back-test reads the full system's parameters
only; no model or simulation is built.
"""

import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import (
    AR_INCOME_TAX_INDEX,
    extend_ar_income_tax_uprating,
    get_ar_cost_of_living_adjustment,
    get_ar_cpi,
    round_ar_income_tax_bound,
)
from policyengine_us.system import system

BOUND_METADATA = {
    "uprating": {
        "parameter": AR_INCOME_TAX_INDEX,
        "rounding": {"type": "nearest", "interval": 100},
    }
}


def synthetic_parameters(annual_levels, bounds=None):
    """CPI-U windows from September 2024, one level per twelve months."""
    monthly = {}
    for offset, level in enumerate(annual_levels):
        start = instant(f"{2024 + offset}-09-01")
        for month in range(12):
            monthly[str(start.offset(month, "month"))] = level
    main = {
        name: {"values": {"2026-01-01": base}, "metadata": BOUND_METADATA}
        for name, base in (bounds or {}).items()
    }
    # A parameter with an earlier history and a non-Arkansas index.
    main["unindexed"] = {"values": {"2026-01-01": 25_000}}
    main["history"] = {
        "values": {"2025-01-01": 5_600, "2026-01-01": 5_600},
        "metadata": BOUND_METADATA,
    }
    return ParameterNode(
        data={
            "gov": {
                "bls": {"cpi": {"cpi_u": {"values": monthly}}},
                "states": {
                    "ar": {
                        "tax": {
                            "income": {
                                "uprating": {"values": {"2014-01-01": 1}},
                                "uprating_cap": {"values": {"2014-01-01": 0.03}},
                                "rates": {"main": main},
                            }
                        }
                    }
                },
            }
        }
    )


def test_ar_cpi_averages_september_through_august():
    parameters = synthetic_parameters((100, 100))
    cpi = parameters.gov.bls.cpi.cpi_u
    # An IRS-style August-July window would include the first poison month
    # and miss August 2026. The following September must also be excluded.
    cpi.update(period="month:2024-08-01:1", value=200)
    cpi.update(period="month:2026-08-01:1", value=124)
    cpi.update(period="month:2026-09-01:1", value=500)

    assert get_ar_cpi(parameters, 2025) == pytest.approx(100)
    # 11 months at 100 and August 2026 at 124: 1,224 / 12 = 102.
    assert get_ar_cpi(parameters, 2026) == pytest.approx(102)
    extend_ar_income_tax_uprating(parameters, end_year=2026)
    # Tax year 2026 takes calendar 2026's adjustment: 102 / 100 - 1 = 2%.
    assert parameters.gov.states.ar.tax.income.uprating("2026-01-01") == pytest.approx(
        1.02
    )


@pytest.mark.parametrize(
    "current_level, expected_index",
    ((99, 1), (100, 1), (101, 1.01), (103, 1.03), (104, 1.03)),
)
def test_ar_index_applies_the_increase_if_any_and_cap(current_level, expected_index):
    parameters = synthetic_parameters((100, current_level))

    extend_ar_income_tax_uprating(parameters, end_year=2026)

    index = parameters.gov.states.ar.tax.income.uprating
    assert index("2025-01-01") == 1
    assert index("2026-01-01") == pytest.approx(expected_index)


def test_ar_index_compounds_each_year_from_the_preceding_index():
    parameters = synthetic_parameters((100, 104, 106.08))

    extend_ar_income_tax_uprating(parameters, end_year=2028)

    index = parameters.gov.states.ar.tax.income.uprating
    # Four percent is capped in 2026, then 106.08 / 104 = 2% in 2027.
    assert index("2026-01-01") == pytest.approx(1.03)
    assert index("2027-01-01") == pytest.approx(1.03 * 1.02)
    # The window after August 2027 repeats 106.08, so 2028 adds nothing.
    assert index("2028-01-01") == pytest.approx(1.03 * 1.02)
    assert index("2029-01-01") == pytest.approx(index("2028-01-01"))


@pytest.mark.parametrize(
    "amount, expected",
    (
        # DFA's ties: 2022 card ($5,000 x 1.03) and 2024 card ($25,000 x 1.03).
        (5_000 * 1.03, 5_100),
        (25_000 * 1.03, 25_700),
        (95_000 * 1.03, 97_800),
        (5_749.99, 5_700),
        (5_750.01, 5_800),
        (5_768, 5_800),
        (0, 0),
    ),
)
def test_ar_bounds_round_to_nearest_100_with_ties_down(amount, expected):
    assert round_ar_income_tax_bound(amount, 100) == expected


def test_ar_index_rounds_each_bound_from_its_2026_value():
    parameters = synthetic_parameters(
        (100, 104, 106.08),
        bounds={"tie": 25_000, "row": 5_600, "threshold": 94_700, "top": 4_700},
    )

    extend_ar_income_tax_uprating(parameters, end_year=2028)

    main = parameters.gov.states.ar.tax.income.rates.main
    # 2026, index 1.03: 25,750 (tie, down), 5,768, 97,541 and 4,841.
    assert main.tie("2026-01-01") == 25_700
    assert main.row("2026-01-01") == 5_800
    assert main.threshold("2026-01-01") == 97_500
    assert main.top("2026-01-01") == 4_800
    # 2027, index 1.0506: 26,265, 5,883.36, 99,491.82 and 4,937.82.
    assert main.tie("2027-01-01") == 26_300
    assert main.row("2027-01-01") == 5_900
    assert main.threshold("2027-01-01") == 99_500
    assert main.top("2027-01-01") == 4_900
    # Earlier years keep the statutory value, whether or not the parameter
    # has a history before 2026.
    assert main.tie("2025-01-01") == 25_000
    assert main.history("2025-01-01") == 5_600
    assert main.history("2026-01-01") == 5_800
    # A parameter not indexed by the Arkansas index is untouched.
    assert main.unindexed("2027-01-01") == 25_000


def test_ar_2026_tables_index_act_1_and_keep_bracket_adjustments_fixed():
    income = system.parameters.gov.states.ar.tax.income
    main = income.rates.main
    # The model's CPI-U gives 3.06% for 2026, capped at 3%.
    assert income.uprating("2026-01-01") == pytest.approx(1.03)
    # Act 1 of 2026's $5,600, $11,200, $16,000 and $26,400 row starts,
    # $94,700 threshold and $4,700 (B) bound, each x 1.03 to the nearest $100.
    assert [b.threshold("2026-01-01") for b in main.rate.brackets[1:5]] == [
        5_800,
        11_500,
        16_500,
        27_200,
    ]
    assert main.high_income.threshold("2026-01-01") == 97_500
    assert main.high_income.rate.brackets[1].threshold("2026-01-01") == 4_800
    # 2025 is DFA's 2025 card, unchanged.
    assert [b.threshold("2025-01-01") for b in main.rate.brackets[1:5]] == [
        5_600,
        11_200,
        16_000,
        26_400,
    ]
    for year in (2026, 2027, 2035):
        assert [
            b.amount(f"{year}-01-01")
            for b in main.high_income.bracket_adjustment.brackets
        ] == list(range(290, -1, -10))


def card_bounds(year):
    """A DFA card's bracket bounds, as recorded in reduction.yaml.

    Row starts are recorded as the bound (for example 4,400) and rows of the
    table above $75,000 as the bound plus 1 (for example 77,401).
    """
    reduction = system.parameters.gov.states.ar.tax.income.rates.main.reduction
    thresholds = [b.threshold(f"{year}-01-01") for b in reduction.brackets]
    finite = [t for t in thresholds if 0 < t < float("inf")]
    return [t - 1 if t % 100 == 1 else t for t in finite]


@pytest.mark.parametrize("year", (2018, 2019, 2020, 2021))
def test_ar_window_reproduces_dfa_cards(year):
    """Each card's bounds index to the next card's, all 11 of them.

    The repository's CPI-U is the not seasonally adjusted series before
    2024, so its windows for 2018-2021 are the statute's: 2.4193%, 1.9000%,
    1.4583% and 2.9977%. The window for tax year Y-1 (the rule Act 1459
    struck) gives 1.9874%, 2.4193%, 1.9000% and 1.4583%, and misses most of
    these bounds. The 2025 card is not tested here: from 2024 the series is
    seasonally adjusted, and across that splice the 2025 window computes to
    2.7265%, not the not seasonally adjusted 2.6531%.
    """
    adjustment = get_ar_cost_of_living_adjustment(system.parameters, year)
    previous = card_bounds(year - 1)
    published = card_bounds(year)
    assert len(previous) == len(published) == 11
    predicted = [
        round_ar_income_tax_bound(bound * (1 + adjustment), 100) for bound in previous
    ]
    assert predicted == published


@pytest.mark.parametrize("year", (2023, 2024))
def test_ar_capped_years_reproduce_dfa_cards(year):
    """2023 and 2024 are capped at 3% under either window; 2024 has a tie.

    The row starts and the high-income threshold (the first row of the
    table above it, less 1) of the previous card, x 1.03, give the card's.
    $25,000 x 1.03 = $25,750 is published as $25,700.
    """
    assert get_ar_cost_of_living_adjustment(system.parameters, year) == 0.03
    previous = card_bounds(year - 1)[:5]
    published = card_bounds(year)[:5]
    predicted = [round_ar_income_tax_bound(bound * 1.03, 100) for bound in previous]
    assert predicted == published
