"""Projection of the Medicaid long-term care home equity limits.

42 USC 1396p(f)(1)(C) increases the limits from year to year by CPI-U,
rounded to the nearest $1,000. ``extend_medicaid_home_equity_limits`` projects
them the way CMS computes them. These tests check that method against CMS's
published bulletins, then check the projected parameter values.

Published figures (CMS SSI and spousal impoverishment bulletins, chart page):
2020 cib062420-new p.2, 2021 cib060421 p.2, 2022 cib06022022_0 p.2,
2025 cib05282025 p.2, 2026 cib04272026 p.2.
"""

import pytest

from policyengine_us.parameters.uprating_extensions import (
    adjust_home_equity_limit_for_inflation,
    get_cms_cpi_u_percentage_increase,
)
from policyengine_us.system import system

CPI = system.parameters.gov.bls.cpi
HOME_EQUITY = system.parameters.gov.hhs.medicaid.eligibility.long_term_care.home_equity

# "CPI Increase for <year>" in each bulletin's chart.
PUBLISHED_CPI_INCREASE = {2020: 1.7, 2021: 1.4, 2022: 5.4, 2025: 2.4, 2026: 3.0}
# (minimum, maximum) home equity limits in each bulletin's chart.
PUBLISHED_LIMITS = {
    2020: (595_000, 893_000),
    2021: (603_000, 906_000),
    2022: (636_000, 955_000),
    2025: (730_000, 1_097_000),
    2026: (752_000, 1_130_000),
}


@pytest.mark.parametrize("year, percentage", PUBLISHED_CPI_INCREASE.items())
def test_cpi_increase_matches_cms(year, percentage):
    assert get_cms_cpi_u_percentage_increase(CPI, year) == percentage


@pytest.mark.parametrize("start, end", [(2020, 2021), (2021, 2022), (2022, 2025)])
@pytest.mark.parametrize("bound", [0, 1])
def test_year_to_year_increases_reproduce_cms_limits(start, end, bound):
    # 2021 separates the methods: $893,000 x 1.014 rounds to $906,000, while
    # the unrounded 1.371% increase would give $905,000. 2022 -> 2025 chains
    # through 2023 and 2024, whose bulletins are not cited here.
    limit = PUBLISHED_LIMITS[start][bound]
    for year in range(start + 1, end + 1):
        limit = adjust_home_equity_limit_for_inflation(
            limit, get_cms_cpi_u_percentage_increase(CPI, year)
        )
    assert limit == PUBLISHED_LIMITS[end][bound]


def test_a_falling_index_is_not_an_increase():
    # The not seasonally adjusted CPI-U fell from September 2014 to
    # September 2015.
    assert CPI.cpi_u("2015-09-01") < CPI.cpi_u("2014-09-01")
    assert get_cms_cpi_u_percentage_increase(CPI, 2016) == 0


def test_published_limits_are_parameter_values():
    for year in (2025, 2026):
        assert HOME_EQUITY.limit(f"{year}-01-01") == PUBLISHED_LIMITS[year][1]
        assert (
            HOME_EQUITY.agricultural_limit(f"{year}-01-01")
            == (PUBLISHED_LIMITS[year][1])
        )


def test_agricultural_limit_is_projected_year_to_year_on_january_1():
    for year in range(2027, 2041):
        current = HOME_EQUITY.agricultural_limit(f"{year}-01-01")
        assert current == adjust_home_equity_limit_for_inflation(
            HOME_EQUITY.agricultural_limit(f"{year - 1}-01-01"),
            get_cms_cpi_u_percentage_increase(CPI, year),
        )
        for month in ["02", "07", "12"]:
            assert HOME_EQUITY.agricultural_limit(f"{year}-{month}-01") == current


def test_non_agricultural_limit_is_the_indexed_maximum_until_the_2028_cap():
    assert HOME_EQUITY.limit("2027-01-01") == HOME_EQUITY.agricultural_limit(
        "2027-01-01"
    )
    for year in range(2028, 2041):
        assert HOME_EQUITY.limit(f"{year}-01-01") == 1_000_000
        assert HOME_EQUITY.agricultural_limit(f"{year}-01-01") > 1_000_000
