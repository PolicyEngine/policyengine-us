"""Projection of the Medicaid long-term care home equity limits.

42 USC 1396p(f)(1)(C) increases the limits from year to year by CPI-U,
rounded to the nearest $1,000. ``extend_medicaid_home_equity_limits`` projects
them the way CMS computes them. These tests check that method against CMS's
published bulletins, then check the projected parameter values.

Published figures (CMS SSI and spousal impoverishment bulletins, chart page):
2020 cib062420-new p.2, 2021 cib060421 p.2, 2022 cib06022022_0 p.2,
2025 cib05282025 p.2, 2026 cib04272026 p.2.
"""

from types import SimpleNamespace

import pytest

from policyengine_us import Simulation
from policyengine_core.parameters import ParameterNode

from policyengine_us.parameters.uprating_extensions import (
    adjust_home_equity_limit_for_inflation,
    extend_medicaid_home_equity_limits,
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


class _Series:
    """A minimal stand-in for a dated CPI parameter."""

    def __init__(self, values):
        self.values = values
        self.values_list = [SimpleNamespace(instant_str=date) for date in values]

    def __call__(self, date):
        return self.values[date]


@pytest.mark.parametrize("current, percentage", [(99.0, 0), (101.0, 1.0)])
def test_a_falling_index_is_not_an_increase(current, percentage):
    cpi = SimpleNamespace(
        cpi_u_nsa_september=_Series({"2030-09-01": 100.0, "2031-09-01": current}),
        cpi_u=None,
    )
    assert get_cms_cpi_u_percentage_increase(cpi, 2032) == percentage


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


def test_chassis_screen_reads_each_years_agricultural_limit():
    # The projected limits move with the CPI-U forecast, so the boundaries are
    # read from the parameters rather than written into a YAML case.
    limit_2028 = HOME_EQUITY.agricultural_limit("2028-01-01")
    limit_2029 = HOME_EQUITY.agricultural_limit("2029-01-01")
    assert limit_2029 > limit_2028
    equity = {"above_2028_limit": limit_2028 + 1, "at_limit": limit_2029}
    equity["above_limit"] = limit_2029 + 1
    people = {
        name: {
            "receives_medicaid_long_term_care_services": {"2029": True},
            "home_is_on_agricultural_land": {"2029": True},
            "home_equity": {"2029": value},
        }
        for name, value in equity.items()
    }
    situation = {"people": people}
    for group in ["tax_units", "spm_units", "families", "marital_units", "households"]:
        situation[group] = {f"{name}_{group}": {"members": [name]} for name in people}
    simulation = Simulation(situation=situation)
    eligible = simulation.calculate(
        "is_medicaid_long_term_care_home_equity_eligible", 2029
    )
    assert eligible.tolist() == [True, True, False]


@pytest.mark.parametrize("agricultural_published_through", [2026, 2027])
def test_non_agricultural_fill_follows_its_own_coverage(
    agricultural_published_through,
):
    # Publishing the 2027 agricultural limit before the non-agricultural one
    # must not leave the non-agricultural 2027 limit at its 2026 value.
    agricultural = {"2025-01-01": 1_097_000, "2026-01-01": 1_130_000}
    if agricultural_published_through == 2027:
        agricultural["2027-01-01"] = 1_164_000
    non_agricultural = {
        "2025-01-01": 1_097_000,
        "2026-01-01": 1_130_000,
        "2028-01-01": 1_000_000,
    }
    septembers = {
        f"{year}-09-01": 100 * 1.03 ** (year - 2024) for year in range(2024, 2031)
    }
    parameters = ParameterNode(
        data={
            "gov": {
                "hhs": {
                    "medicaid": {
                        "eligibility": {
                            "long_term_care": {
                                "home_equity": {
                                    "agricultural_limit": {"values": agricultural},
                                    "limit": {"values": non_agricultural},
                                }
                            }
                        }
                    }
                },
                "bls": {
                    "cpi": {
                        "cpi_u_nsa_september": {"values": septembers},
                        "cpi_u": {"values": septembers},
                    }
                },
            }
        }
    )
    extend_medicaid_home_equity_limits(parameters, end_year=2030)
    home_equity = parameters.gov.hhs.medicaid.eligibility.long_term_care.home_equity
    assert home_equity.limit("2027-01-01") == home_equity.agricultural_limit(
        "2027-01-01"
    )
    assert home_equity.limit("2027-01-01") > 1_130_000
    assert home_equity.limit("2028-01-01") == 1_000_000
    assert home_equity.agricultural_limit(
        "2028-01-01"
    ) == adjust_home_equity_limit_for_inflation(
        home_equity.agricultural_limit("2027-01-01"), 3.0
    )
