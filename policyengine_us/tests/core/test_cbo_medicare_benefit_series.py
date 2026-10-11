"""The per-enrollee series that ``cbo_medicare_benefit`` subtracts.

CBO counts Medicare in household income at the government's average cost
per enrollee, net of premiums paid by enrollees, and counts the Part D
low-income subsidy separately. ``cbo_medicare_benefit`` takes CMS Medicare
spending per enrollee (``calibration.gov.hhs.medicare.per_capita_cost``) less
the low-income subsidy, scales it to enrollees outside nursing homes
(``noninstitutionalized_spending_ratio``), and subtracts the premium series.
All four series under ``calibration.gov.hhs.medicare`` are aggregates from
the 2026 Medicare Trustees Report over Table V.B3's total enrollment (people
with Part A and/or Part B):

- ``premium_income_per_enrollee.part_a``: Table III.B4 premiums from
  voluntary enrollees.
- ``premium_income_per_enrollee.part_b``: Table III.C7 incurred premium
  income through 2026, then Table III.C4 cash premium income, with the
  December 31, 2026 credit moved back to 2027.
- ``premium_income_per_enrollee.part_d``: Table III.D3 premium income with
  footnote 6's December 31 credits moved back a year.
- ``part_d_low_income_subsidy_per_enrollee``: Table IV.B10 low-income
  subsidy (the 2025 report for 2015).

These tests read parameters only; the YAML tests cover the variable.

Invariants:

1. Transcription: every value equals its formula applied to the Trustees'
   published cells, rounded as stored.
2. Conservation: each series times total enrollment returns its published
   aggregate, within the cells' rounding.
3. Differential: the Part D series equals the Part D enrollment share times
   ``part_d.premiums_per_enrollee`` (which excludes income-related premiums,
   per Part D enrollee) plus Table V.E4's income-related premiums per
   Medicare enrollee: two derivations from different cells agree.
4. Part B premium income includes income-related premiums: in 2019 the
   standard premium times Part B enrollment plus Table V.E3's aggregate
   income-related premiums reproduces it within 0.5 percent, while the
   standard premium alone falls more than 5 percent short.
5. Bounds: every series is positive, and net Medicare spending per enrollee,
   (spending - low-income subsidy) x the noninstitutionalized ratio -
   premiums, stays between 0 and scaled gross spending, in every year from
   2015 to 2200.
6. Extension: from 2036 to 2100 each series grows with Medicare spending
   per enrollee, so each keeps its 2035 share of spending; later years hold
   the 2100 value.
7. Calendar years: every date in a year reads the January 1 value.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

MEDICARE = "calibration.gov.hhs.medicare"
SERIES = {
    "part_a": f"{MEDICARE}.premium_income_per_enrollee.part_a",
    "part_b": f"{MEDICARE}.premium_income_per_enrollee.part_b",
    "part_d": f"{MEDICARE}.premium_income_per_enrollee.part_d",
    "lis": f"{MEDICARE}.part_d_low_income_subsidy_per_enrollee",
}
SPENDING = f"{MEDICARE}.per_capita_cost"
RATIO = f"{MEDICARE}.noninstitutionalized_spending_ratio"
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2015, 2035, 2100
YEARS = range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1)


def _cells(*values):
    return dict(zip(YEARS, values))


# 2026 Medicare Trustees Report (sha256 ffa56b91...8fa8), file pages.
# Table V.B3 (page 196), total enrollment, thousands.
TOTAL_ENROLLMENT = _cells(
    *(55_589, 57_073, 58_683, 60_020, 61_535, 62_887, 63_980, 65_166),
    *(66_606, 68_066, 69_289, 70_743, 72_322, 74_026, 75_436, 76_598),
    *(77_521, 78_327, 79_058, 79_827, 80_632),
)
# Table III.B4 (page 64), premiums from voluntary enrollees, $ billions.
PART_A_PREMIUMS = _cells(
    *(3.2, 3.3, 3.5, 3.6, 3.9, 4.0, 4.2, 4.5, 4.7, 4.8, 5.7),
    *(6.9, 7.4, 7.9, 8.5, 9.0, 9.7, 10.3, 11.1, 11.9, 12.6),
)
# Table III.C7 (page 102), premium income, incurred basis, $ millions.
PART_B_INCURRED = dict(
    zip(
        range(2015, 2027),
        (
            *(67_515, 73_986, 81_522, 93_312, 99_413, 108_746, 113_411),
            *(130_941, 131_166, 139_837, 150_318, 173_228),
        ),
    )
)
# Table III.C4 (page 96), premium income, cash basis, $ billions.
PART_B_CASH = _cells(
    *(69.4, 72.1, 81.5, 93.3, 99.4, 111.2, 111.0, 130.9, 131.2, 139.8, 150.3),
    *(174.8, 182.8, 204.0, 222.3, 243.5, 264.3, 286.9, 315.1, 346.0, 375.1),
)
# Table III.D3 (page 116), premium income, cash basis, $ billions, and
# footnote 6's December 31 credits (page 117).
PART_D_CASH = _cells(
    *(12.7, 13.8, 15.5, 15.9, 15.7, 15.8, 17.0, 17.6, 18.3, 19.2, 14.9),
    *(20.1, 25.6, 28.8, 30.5, 51.7, 54.9, 56.4, 59.5, 62.0, 65.3),
)
PART_D_DECEMBER_31_CREDIT = {2015: 0.2, 2020: 0.1, 2026: 0.2}
# Table IV.B10 (page 159), low-income subsidy, $ billions; 2015 from the
# 2025 report's Table IV.B10 (page 159).
LOW_INCOME_SUBSIDY = _cells(
    *(25.6, 26.4, 27.3, 28.5, 29.7, 33.0, 35.0, 39.4, 44.2, 41.2, 17.4),
    *(18.1, 20.5, 22.1, 24.5, 28.9, 30.7, 31.7, 32.4, 33.3, 34.8),
)
# Table V.E4 (page 218), Part D income-related premiums, $ billions.
PART_D_IRMAA = _cells(
    *(0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 1.8, 1.7, 2.2, 2.2, 2.4, 3.1, 3.5),
    *(4.0, 4.6, 10.8, 11.9, 12.6, 13.7, 14.7, 15.9),
)
# 2019: Table III.C2 (page 89) standard monthly premium, Table V.B3 Part B
# enrollment (thousands), Table V.E3 (page 215) income-related premiums
# ($ billions).
STANDARD_PART_B_PREMIUM_2019 = 135.50
PART_B_ENROLLMENT_2019 = 56_019
PART_B_IRMAA_2019 = 8.4


def _part_b_billions(year):
    if year in PART_B_INCURRED:
        return PART_B_INCURRED[year] / 1e3
    # III.C4 footnote 7: January 2027 withholdings credited December 31, 2026.
    december_31_credit = PART_B_CASH[2026] - PART_B_INCURRED[2026] / 1e3
    return PART_B_CASH[year] + (december_31_credit if year == 2027 else 0)


def _part_d_billions(year):
    return (
        PART_D_CASH[year]
        - PART_D_DECEMBER_31_CREDIT.get(year, 0)
        + PART_D_DECEMBER_31_CREDIT.get(year - 1, 0)
    )


AGGREGATES = {
    "part_a": PART_A_PREMIUMS.get,
    "part_b": _part_b_billions,
    "part_d": _part_d_billions,
    "lis": LOW_INCOME_SUBSIDY.get,
}


def _read(name, date):
    return get_parameter(system.parameters, name)(date)


def _value(series, year):
    return _read(SERIES[series], f"{year}-01-01")


def _spending(year):
    return _read(SPENDING, f"{year}-01-01")


def _per_enrollee(billions, year):
    return billions * 1e9 / (TOTAL_ENROLLMENT[year] * 1e3)


@pytest.mark.parametrize("series", SERIES)
@pytest.mark.parametrize("year", YEARS)
def test_series_is_the_trustees_aggregate_per_medicare_enrollee(series, year):
    expected = _per_enrollee(AGGREGATES[series](year), year)
    assert _value(series, year) == round(expected, 2)


@pytest.mark.parametrize("series", SERIES)
@pytest.mark.parametrize("year", YEARS)
def test_series_times_enrollment_returns_the_aggregate(series, year):
    rebuilt = _value(series, year) * TOTAL_ENROLLMENT[year] * 1e3 / 1e9
    # Stored to the cent; enrollment of at most 81 million moves the
    # aggregate by at most $0.0005 billion.
    assert rebuilt == pytest.approx(AGGREGATES[series](year), abs=1e-3)


@pytest.mark.parametrize("year", YEARS)
def test_part_d_series_matches_share_times_premium_plus_irmaa(year):
    share = _read(f"{MEDICARE}.part_d.enrollment_share", f"{year}-01-01")
    premium = _read(f"{MEDICARE}.part_d.premiums_per_enrollee", f"{year}-01-01")
    irmaa = _per_enrollee(PART_D_IRMAA[year], year)
    # The share is stored to four decimals and the premium to the cent, so
    # the product can be off by up to about $0.05.
    assert share * premium + irmaa == pytest.approx(_value("part_d", year), abs=0.1)


def test_part_b_premium_income_includes_income_related_premiums():
    standard = STANDARD_PART_B_PREMIUM_2019 * 12 * PART_B_ENROLLMENT_2019 * 1e3 / 1e9
    published = _part_b_billions(2019)
    assert standard + PART_B_IRMAA_2019 == pytest.approx(published, rel=0.005)
    assert standard < published * 0.95


@given(st.integers(FIRST_YEAR, END_YEAR + 100))
def test_series_are_positive_and_net_spending_is_between_zero_and_gross(year):
    ratio = _read(RATIO, f"{year}-01-01")
    premiums = sum(_value(series, year) for series in SERIES if series != "lis")
    net = (_spending(year) - _value("lis", year)) * ratio - premiums
    assert all(_value(series, year) > 0 for series in SERIES)
    assert 0 < net < _spending(year) * ratio


@pytest.mark.parametrize("series", SERIES)
def test_extension_keeps_the_2035_share_of_spending(series):
    share_2035 = _value(series, LAST_PROJECTED_YEAR) / _spending(LAST_PROJECTED_YEAR)
    for year in range(LAST_PROJECTED_YEAR + 1, END_YEAR + 1):
        assert _value(series, year) / _spending(year) == pytest.approx(
            share_2035, rel=1e-9
        )


@given(st.integers(END_YEAR, END_YEAR + 100))
def test_series_hold_the_2100_values_afterwards(year):
    for series in SERIES:
        assert _value(series, year) == _value(series, END_YEAR)


@given(st.integers(FIRST_YEAR, END_YEAR), st.integers(1, 12), st.integers(1, 28))
def test_every_date_in_a_year_reads_the_january_value(year, month, day):
    date = f"{year}-{month:02d}-{day:02d}"
    for series in SERIES:
        assert _read(SERIES[series], date) == _value(series, year)
