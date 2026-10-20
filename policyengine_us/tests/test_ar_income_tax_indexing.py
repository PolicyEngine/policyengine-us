"""Arkansas's statutory CPI-U window, cap, floor, and annual compounding."""

import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import (
    extend_ar_income_tax_uprating,
    get_ar_cpi,
)
from policyengine_us.system import system
from policyengine_us.tests.fixtures.ar_indexing import (
    ar_cpi_four_percent_chained_one_percent,
)


def synthetic_parameters(annual_levels):
    monthly = {}
    for offset, level in enumerate(annual_levels):
        start = instant(f"{2024 + offset}-09-01")
        for month in range(12):
            monthly[str(start.offset(month, "month"))] = level
    return ParameterNode(
        data={
            "gov": {
                "bls": {"cpi": {"cpi_u": {"values": monthly}}},
                "states": {
                    "ar": {
                        "tax": {
                            "income": {
                                "uprating": {"values": {"2026-01-01": 1}},
                                "uprating_cap": {"values": {"2014-01-01": 0.03}},
                            }
                        }
                    }
                },
            }
        }
    )


@pytest.fixture(scope="module")
def capped_parameters():
    """Read-only reformed parameters shared by the Core integration checks."""
    return ar_cpi_four_percent_chained_one_percent(system).parameters


def test_ar_cpi_averages_september_through_august():
    parameters = synthetic_parameters((100, 100))
    cpi = parameters.gov.bls.cpi.cpi_u
    # An IRS-style August-July window would include the first poison month
    # and miss August 2026. The following September must also be excluded.
    cpi.update(period="month:2024-08-01:1", value=200)
    cpi.update(period="month:2026-08-01:1", value=124)
    cpi.update(period="month:2026-09-01:1", value=500)

    assert get_ar_cpi(parameters, 2025) == pytest.approx(100)
    assert get_ar_cpi(parameters, 2026) == pytest.approx(102)
    extend_ar_income_tax_uprating(parameters, end_year=2027)
    assert parameters.gov.states.ar.tax.income.uprating("2027-01-01") == pytest.approx(
        1.02
    )


@pytest.mark.parametrize(
    "current_level, expected_index",
    ((99, 1), (100, 1), (101, 1.01), (103, 1.03), (104, 1.03)),
)
def test_ar_index_applies_the_increase_if_any_and_cap(current_level, expected_index):
    parameters = synthetic_parameters((100, current_level))

    extend_ar_income_tax_uprating(parameters, end_year=2027)

    assert parameters.gov.states.ar.tax.income.uprating("2027-01-01") == pytest.approx(
        expected_index
    )


def test_ar_index_compounds_each_year_from_the_preceding_index():
    parameters = synthetic_parameters((100, 104, 106.08))

    extend_ar_income_tax_uprating(parameters, end_year=2028)

    index = parameters.gov.states.ar.tax.income.uprating
    assert index("2026-01-01") == 1
    assert index("2027-01-01") == pytest.approx(1.03)
    # Four percent is capped in 2027, then two percent compounds in 2028.
    assert index("2028-01-01") == pytest.approx(1.03 * 1.02)
    assert index("2029-01-01") == pytest.approx(index("2028-01-01"))


def test_ar_index_and_irs_index_remain_independent(capped_parameters):
    ar_index = capped_parameters.gov.states.ar.tax.income.uprating
    irs_index = capped_parameters.gov.irs.uprating

    assert ar_index("2027-01-01") / ar_index("2026-01-01") == pytest.approx(1.03)
    assert irs_index("2027-01-01") / irs_index("2026-01-01") == pytest.approx(1.01)


def test_ar_published_tables_and_fixed_bracket_adjustments_are_preserved(
    capped_parameters,
):
    original = system.parameters.gov.states.ar.tax.income.rates.main
    reformed = capped_parameters.gov.states.ar.tax.income.rates.main

    for year in range(2014, 2027):
        period = f"{year}-01-01"
        assert [b.threshold(period) for b in reformed.rate.brackets] == [
            b.threshold(period) for b in original.rate.brackets
        ]
    assert [b.threshold("2026-01-01") for b in reformed.rate.brackets[1:5]] == [
        5_600,
        11_200,
        16_000,
        26_400,
    ]
    assert reformed.high_income.threshold("2026-01-01") == 94_700
    assert reformed.high_income.threshold("2027-01-01") == 97_500
    assert reformed.high_income.rate.brackets[1].threshold("2027-01-01") == 4_800
    assert [
        b.amount("2027-01-01") for b in reformed.high_income.bracket_adjustment.brackets
    ] == list(range(290, -1, -10))
