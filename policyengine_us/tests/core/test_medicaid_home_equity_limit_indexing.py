"""Indexing of the Medicaid long-term care home equity limits.

42 USC 1396p(f)(1)(C) increases the limits from year to year by CPI-U,
rounded to the nearest $1,000. CMS applies the September-to-September change
each January 1. These tests check that the parameters follow that method and
that the hand-entered 2027 non-agricultural projection agrees with the
uprated agricultural limit, which is the same indexed amount before P.L.
119-21 section 71108 caps non-agricultural homes at $1,000,000 in 2028.
"""

import pytest

from policyengine_us.system import system

HOME_EQUITY = system.parameters.gov.hhs.medicaid.eligibility.long_term_care.home_equity
CPI_U = system.parameters.gov.bls.cpi.cpi_u


def indexed(value, year):
    change = CPI_U(f"{year - 1}-09-01") / CPI_U(f"{year - 2}-09-01")
    return round(value * change / 1_000) * 1_000


@pytest.mark.parametrize("name", ["limit", "agricultural_limit"])
def test_cms_method_reproduces_the_published_2026_limit(name):
    parameter = getattr(HOME_EQUITY, name)
    # CMS published $1,097,000 for 2025 and $1,130,000 for 2026.
    assert indexed(parameter("2025-01-01"), 2026) == parameter("2026-01-01")


def test_agricultural_limit_steps_only_on_january_1():
    for year in range(2027, 2041):
        prior = HOME_EQUITY.agricultural_limit(f"{year - 1}-01-01")
        current = HOME_EQUITY.agricultural_limit(f"{year}-01-01")
        assert current == indexed(prior, year), year
        for month in ["02", "07", "12"]:
            assert HOME_EQUITY.agricultural_limit(f"{year}-{month}-01") == current


def test_2027_non_agricultural_projection_matches_the_uprated_limit():
    projected = HOME_EQUITY.limit("2027-01-01")
    uprated = HOME_EQUITY.agricultural_limit("2027-01-01")
    assert projected == uprated, (
        "home_equity/limit.yaml's 2027 value is a CPI-U projection; set it to "
        f"{uprated:,.0f}, the uprated agricultural limit, or to the CMS figure "
        "once published (and add that figure to agricultural_limit.yaml too)."
    )


def test_non_agricultural_cap_holds_from_2028():
    for year in range(2028, 2041):
        assert HOME_EQUITY.limit(f"{year}-01-01") == 1_000_000
        assert HOME_EQUITY.agricultural_limit(f"{year}-01-01") > 1_000_000
