"""The HSA contribution limits in 26 U.S.C. 223(b)(2) and their 223(g)
indexation.

``health_savings_account_payroll_contributions`` uprates by the family limit,
so these tests check the series an input follows as well as the law.

Invariants:

1. Transcription: the parameters hold the self-only and family limits the IRS
   published for each year.
2. Differential: an independent implementation of 223(g), written here from
   the monthly BLS values in ``gov.bls.cpi`` with every index averaged over
   the 12 months ending March 31 (223(g)(1) applies 1(f)(4) "by substituting
   'March 31' for 'August 31'"), reproduces 15 of the 18 limits published
   for 2019 to 2027: the 2019 and 2023 family limits and the 2025 self-only
   limit come out $50 lower. Taking only the 1(f)(3)(B) ratio for 2016 over
   the 12 months ending August 31 reproduces all 18. The published limits
   are encoded for their own years either way, so the window choice only
   moves the projections. Both reproduce the 2018 limits of Rev. Proc.
   2018-18; the family parameter instead holds the $6,900 that Rev. Proc.
   2018-27 let taxpayers use (an intended difference). The model's
   ``get_hsa_cola`` agrees with the March implementation in every year whose
   window is observed.
3. Extension rule: every year after the last IRS publication equals the
   statutory base plus the adjustment applied to it, rounded to the nearest
   $50.
4. Bounds and order (Hypothesis): both limits are positive multiples of $50,
   never fall from one year to a later one, a projected limit never falls
   while the index it reads doesn't, the family limit is at least the
   self-only limit and within $50 of twice it. The March-window price index the
   projection reads is positive and rises in every projected year.
"""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.parameters.uprating_extensions import (
    HSA_CONTRIBUTION_LIMIT_STATUTORY_BASES,
    get_average_for_12_months_ending_march,
    get_hsa_cola,
)
from policyengine_us.system import system

LIMIT = "gov.irs.gross_income.health_savings_account_contributions.limit"
END_YEAR = 2100
BASES = dict(HSA_CONTRIBUTION_LIMIT_STATUTORY_BASES)

# (self-only, family) limits from the IRS publication for each year: Notice
# 2004-2 (2004), then the Rev. Proc. for each year cited in the parameter files
# (Rev. Proc. 2004-71 for 2005 through Rev. Proc. 2026-24 for 2027).
PUBLISHED = {
    2004: (2_600, 5_150),
    2005: (2_650, 5_250),
    2006: (2_700, 5_450),
    2007: (2_850, 5_650),
    2008: (2_900, 5_800),
    2009: (3_000, 5_950),
    2010: (3_050, 6_150),
    2011: (3_050, 6_150),
    2012: (3_100, 6_250),
    2013: (3_250, 6_450),
    2014: (3_300, 6_550),
    2015: (3_350, 6_650),
    2016: (3_350, 6_750),
    2017: (3_400, 6_750),
    # Rev. Proc. 2018-27 restored the $6,900 family limit that Rev. Proc.
    # 2018-18 had cut to $6,850.
    2018: (3_450, 6_900),
    2019: (3_500, 7_000),
    2020: (3_550, 7_100),
    2021: (3_600, 7_200),
    2022: (3_650, 7_300),
    2023: (3_850, 7_750),
    2024: (4_150, 8_300),
    2025: (4_300, 8_550),
    2026: (4_400, 8_750),
    2027: (4_500, 9_000),
}
LAST_PUBLISHED_YEAR = max(PUBLISHED)
# Years the C-CPI-U-based 223(g) (after Pub. L. 115-97) governs.
CHAINED_YEARS = range(2018, LAST_PUBLISHED_YEAR + 1)
REV_PROC_2018_18 = (3_450, 6_850)


def _limit(name, year):
    return get_parameter(system.parameters, f"{LIMIT}.{name}")(f"{year}-01-01")


def _monthly(path, year, month):
    return get_parameter(system.parameters, path)(f"{year}-{month:02d}-01")


def _window_average(path, year, last_month):
    """Average of the 12 monthly values ending in ``last_month`` of ``year``.

    BLS did not publish October 2025; the parameter carries the September
    value at that instant, which is what this reads.
    """
    months = [
        (year - (month <= 0), (month - 1) % 12 + 1)
        for month in range(last_month - 11, last_month + 1)
    ]
    return sum(_monthly(path, y, m) for y, m in months) / 12


def _independent_cola(tax_year, ratio_window_end=3):
    """223(g)(1) adjustment; ``ratio_window_end`` is the last month of the
    windows for the 2016 C-CPI-U/CPI ratio (3 for March, 8 for August)."""
    cpi_u, c_cpi_u = "gov.bls.cpi.cpi_u", "gov.bls.cpi.c_cpi_u"
    ratio_2016 = _window_average(c_cpi_u, 2016, ratio_window_end) / _window_average(
        cpi_u, 2016, ratio_window_end
    )
    denominator = _window_average(cpi_u, 1997, 3) * ratio_2016
    return _window_average(c_cpi_u, tax_year - 1, 3) / denominator - 1


# Published limits the March recipe misses, each by $50: (year, coverage).
MARCH_RECIPE_MISSES = {
    (2019, "family"): 6_950,
    (2023, "family"): 7_700,
    (2025, "self_only"): 4_250,
}


def _statutory_limit(base, cola):
    return base + math.floor(base * cola / 50 + 0.5) * 50


@pytest.mark.parametrize("year", sorted(PUBLISHED))
def test_parameters_hold_the_published_limits(year):
    assert (_limit("self_only", year), _limit("family", year)) == PUBLISHED[year]


@pytest.mark.parametrize("year", CHAINED_YEARS)
def test_march_recipe_against_the_published_limits(year):
    cola = _independent_cola(year)
    expected = REV_PROC_2018_18 if year == 2018 else PUBLISHED[year]
    for (name, base), published in zip(BASES.items(), expected):
        computed = _statutory_limit(base, cola)
        assert computed == MARCH_RECIPE_MISSES.get((year, name), published)
        assert published - computed in (0, 50)


@pytest.mark.parametrize("year", CHAINED_YEARS)
def test_august_ratio_variant_reproduces_the_published_limits(year):
    # Not the model's recipe: recorded so a change in either variant's fit
    # shows up.
    cola = _independent_cola(year, ratio_window_end=8)
    computed = tuple(_statutory_limit(BASES[name], cola) for name in BASES)
    expected = REV_PROC_2018_18 if year == 2018 else PUBLISHED[year]
    assert computed == expected


@pytest.mark.parametrize("year", CHAINED_YEARS)
def test_model_cola_matches_the_independent_implementation(year):
    assert get_hsa_cola(system.parameters, year) == pytest.approx(
        _independent_cola(year), rel=1e-12
    )


@given(st.integers(LAST_PUBLISHED_YEAR + 1, END_YEAR))
def test_projected_limits_follow_the_statute(year):
    cola = get_hsa_cola(system.parameters, year)
    for name, base in BASES.items():
        assert _limit(name, year) == _statutory_limit(base, cola)


@given(
    st.sampled_from(sorted(BASES)),
    st.integers(min(PUBLISHED), END_YEAR),
    st.integers(0, END_YEAR - min(PUBLISHED)),
)
def test_limits_are_positive_multiples_of_50_that_never_fall(name, year, gap):
    later = min(year + gap, END_YEAR)
    assert 0 < _limit(name, year) <= _limit(name, later)
    assert _limit(name, year) % 50 == 0


@given(st.integers(min(PUBLISHED), END_YEAR))
def test_family_limit_is_within_50_of_twice_the_self_only_limit(year):
    assert _limit("family", year) >= _limit("self_only", year)
    assert abs(_limit("family", year) - 2 * _limit("self_only", year)) <= 50


@given(
    st.sampled_from(sorted(BASES)),
    st.integers(LAST_PUBLISHED_YEAR + 1, END_YEAR),
    st.integers(0, END_YEAR - LAST_PUBLISHED_YEAR - 1),
)
def test_projected_limit_never_falls_while_the_index_does_not(name, year, gap):
    later = min(year + gap, END_YEAR)
    c_cpi_u = system.parameters.gov.bls.cpi.c_cpi_u
    if get_average_for_12_months_ending_march(
        c_cpi_u, later - 1
    ) >= get_average_for_12_months_ending_march(c_cpi_u, year - 1):
        assert _limit(name, year) <= _limit(name, later)


@given(
    # The C-CPI-U starts in December 1999, so its first full window ends in
    # March 2001.
    st.sampled_from([("cpi_u", 1997), ("c_cpi_u", 2001)]).flatmap(
        lambda series: st.tuples(st.just(series[0]), st.integers(series[1], END_YEAR))
    )
)
def test_march_window_index_is_positive(series_and_year):
    series, year = series_and_year
    cpi = getattr(system.parameters.gov.bls.cpi, series)
    assert get_average_for_12_months_ending_march(cpi, year) > 0


@given(st.integers(LAST_PUBLISHED_YEAR, END_YEAR - 1))
def test_march_window_index_rises_in_every_projected_year(year):
    c_cpi_u = system.parameters.gov.bls.cpi.c_cpi_u
    assert get_average_for_12_months_ending_march(
        c_cpi_u, year
    ) < get_average_for_12_months_ending_march(c_cpi_u, year + 1)
