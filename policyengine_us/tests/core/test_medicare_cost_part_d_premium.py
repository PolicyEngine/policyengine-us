"""The expected Part D premium that ``medicare_cost`` subtracts.

CMS Medicare spending per enrollee (``calibration.gov.hhs.medicare.
per_capita_cost``, scaled by ``noninstitutionalized_spending_ratio`` to
enrollees outside nursing homes) covers Parts A through D, gross of the
premiums that finance it. No variable records Part D enrollment, so
``medicare_cost`` subtracts an expected Part D premium:

    enrollment_share x (premiums_per_enrollee + Part D IRMAA)

from two series under ``calibration.gov.hhs.medicare.part_d``, both from the
2026 Medicare Trustees Report:

- ``premiums_per_enrollee``: Table III.D3 premium income (footnote 6's
  December 31 credits moved back a year) less Table V.E4's aggregate
  income-related premiums, over Table V.B3's Part D enrollment.
- ``enrollment_share``: Table V.B3's Part D enrollment over its total, people
  with Part A and/or Part B coverage.

Invariants:

1. Transcription: every value equals its formula applied to the Trustees'
   published cells, rounded as stored.
2. Conservation: premiums per Part D enrollee times Part D enrollment, plus
   aggregate IRMAA, returns Table III.D3's premium income in every year from
   2015 to 2035, within the tables' rounding.
3. Bounds: the share lies strictly between 0 and 1 and premiums are
   positive in every year from 2015 to 2200. The monthly premium per Part D
   enrollee is below the Trustees' average paid premium in 2025 and 2026,
   since low-income subsidy enrollees pay less or nothing.
4. Extension: each year from 2036 to 2100 equals the 2035 value times
   (722.05 / 699.07) ** (year - 2035), and later years hold the 2100 value.
   That growth is within half a point of the Trustees' 2035 growth in Part D
   cost per beneficiary (Table V.D1).
5. Calendar years: every date in a year reads the January 1 value; between
   the Trustees' five-year enrollment points the share holds the earlier one.
6. Consumer (Hypothesis, differential): ``medicare_cost`` equals a reference
   implementation, max(gross - Part A - Part B - share x (premium + IRMAA),
   0) with gross = per_capita_cost x the ratio, for any year and premiums; it lies in [0, ``medicare_gross_cost``],
   which does not change with the Part D premium; and it does not rise with
   the person's Part D IRMAA.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system

PREMIUM = "calibration.gov.hhs.medicare.part_d.premiums_per_enrollee"
SHARE = "calibration.gov.hhs.medicare.part_d.enrollment_share"
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2015, 2035, 2100
PROJECTED_YEARS = range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1)

# 2026 Medicare Trustees Report (sha256 ffa56b91...8fa8).
# Table III.D3 (file page 116), premium income, $ billions, cash basis.
PREMIUM_INCOME = dict(
    zip(
        PROJECTED_YEARS,
        (
            *(12.7, 13.8, 15.5, 15.9, 15.7, 15.8, 17.0, 17.6, 18.3, 19.2, 14.9),
            *(20.1, 25.6, 28.8, 30.5, 51.7, 54.9, 56.4, 59.5, 62.0, 65.3),
        ),
    )
)
# Footnote 6 (file page 117): premiums withheld from January benefits that
# were credited on December 31 of the year before, $ billions.
DECEMBER_31_CREDIT = {2015: 0.2, 2020: 0.1, 2026: 0.2}
# Table V.E4 (file page 218), aggregate income-related premiums, $ billions.
IRMAA_AGGREGATE = dict(
    zip(
        PROJECTED_YEARS,
        (
            *(0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 1.8, 1.7, 2.2, 2.2, 2.4, 3.1, 3.5),
            *(4.0, 4.6, 10.8, 11.9, 12.6, 13.7, 14.7, 15.9),
        ),
    )
)
# Table V.B3 (file page 196), enrollment in thousands: annual through 2035,
# then every fifth year.
ENROLLMENT_YEARS = (*PROJECTED_YEARS, *range(2040, END_YEAR + 1, 5))
PART_D_ENROLLMENT = dict(
    zip(
        ENROLLMENT_YEARS,
        (
            *(41_786, 43_198, 44_475, 45_798, 47_179, 48_696, 49_976, 51_386),
            *(52_893, 55_249, 56_754, 57_973, 59_700, 61_448, 62_975, 64_201),
            *(65_224, 66_111, 66_899, 67_661, 68_416, 70_471, 71_528, 72_969),
            *(75_043, 77_612, 80_085, 82_775, 85_396, 87_208, 88_382, 88_728),
            *(88_845, 89_095),
        ),
    )
)
TOTAL_ENROLLMENT = dict(
    zip(
        ENROLLMENT_YEARS,
        (
            *(55_589, 57_073, 58_683, 60_020, 61_535, 62_887, 63_980, 65_166),
            *(66_606, 68_066, 69_289, 70_743, 72_322, 74_026, 75_436, 76_598),
            *(77_521, 78_327, 79_058, 79_827, 80_632, 82_606, 83_648, 85_413),
            *(87_929, 90_916, 93_612, 96_634, 99_585, 101_485, 102_662),
            *(102_816, 102_848, 103_133),
        ),
    )
)
# Average paid premium per month (file page 217).
AVERAGE_PAID_PREMIUM = {2025: 23.95, 2026: 27.22}
# Table V.D1 (file page 210), Part D average per beneficiary cost.
PART_D_COST_PER_BENEFICIARY = {2034: 4_919, 2035: 5_074}

years = st.integers(FIRST_YEAR, END_YEAR)


def _read(name, date):
    return get_parameter(system.parameters, name)(date)


def _premium(year):
    return _read(PREMIUM, f"{year}-01-01")


def _share(year):
    return _read(SHARE, f"{year}-01-01")


def _accrual_premium_income(year):
    return (
        PREMIUM_INCOME[year]
        - DECEMBER_31_CREDIT.get(year, 0)
        + DECEMBER_31_CREDIT.get(year - 1, 0)
    )


@pytest.mark.parametrize("year", PROJECTED_YEARS)
def test_premium_is_trustees_premium_income_net_of_irmaa_per_part_d_enrollee(year):
    billions = _accrual_premium_income(year) - IRMAA_AGGREGATE[year]
    expected = billions * 1e9 / (PART_D_ENROLLMENT[year] * 1e3)
    assert _premium(year) == round(expected, 2)


@pytest.mark.parametrize("year", ENROLLMENT_YEARS)
def test_share_is_trustees_part_d_over_total_enrollment(year):
    assert _share(year) == round(PART_D_ENROLLMENT[year] / TOTAL_ENROLLMENT[year], 4)


@pytest.mark.parametrize("year", PROJECTED_YEARS)
def test_premiums_and_irmaa_return_trustees_premium_income(year):
    """Conservation: the series, scaled back up by enrollment, plus IRMAA
    gives the published premium income, within rounding of the cells."""
    rebuilt = _premium(year) * PART_D_ENROLLMENT[year] * 1e3 / 1e9
    rebuilt += IRMAA_AGGREGATE[year]
    # Each cell is rounded to $0.1 billion, the stored value to the cent.
    assert rebuilt == pytest.approx(_accrual_premium_income(year), abs=1e-3)
    assert abs(rebuilt - PREMIUM_INCOME[year]) <= 0.2 + 1e-3


@pytest.mark.parametrize("year", sorted(AVERAGE_PAID_PREMIUM))
def test_monthly_premium_is_below_the_average_paid_premium(year):
    assert _premium(year) / 12 < AVERAGE_PAID_PREMIUM[year]


@given(st.integers(FIRST_YEAR, END_YEAR + 100))
def test_share_and_premium_are_bounded(year):
    assert 0 < _share(year) < 1
    assert _premium(year) > 0


def test_extension_rate_follows_trustees_part_d_cost_growth():
    growth = _premium(LAST_PROJECTED_YEAR + 1) / _premium(LAST_PROJECTED_YEAR)
    trustees = PART_D_COST_PER_BENEFICIARY[2035] / PART_D_COST_PER_BENEFICIARY[2034]
    assert abs(growth - trustees) < 0.005


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_extension_is_the_closed_form_of_the_2034_2035_growth(year):
    growth = _premium(LAST_PROJECTED_YEAR) / _premium(LAST_PROJECTED_YEAR - 1)
    expected = _premium(LAST_PROJECTED_YEAR) * growth ** (year - LAST_PROJECTED_YEAR)
    assert _premium(year) == pytest.approx(expected, rel=1e-9)


@given(st.integers(END_YEAR, END_YEAR + 100))
def test_series_hold_the_2100_values_afterwards(year):
    assert _premium(year) == _premium(END_YEAR)
    assert _share(year) == _share(END_YEAR)


@given(years, st.integers(1, 12), st.integers(1, 28))
def test_every_date_in_a_year_reads_the_january_value(year, month, day):
    date = f"{year}-{month:02d}-{day:02d}"
    assert _read(PREMIUM, date) == _premium(year)
    assert _read(SHARE, date) == _share(year)


@given(st.integers(LAST_PROJECTED_YEAR, END_YEAR))
def test_share_holds_the_latest_trustees_point(year):
    point = max(y for y in ENROLLMENT_YEARS if y <= year)
    assert _share(year) == _share(point)


def _simulation(year, people):
    names = list(people)
    return Simulation(
        situation={
            "people": people,
            "tax_units": {f"tax_unit_{name}": {"members": [name]} for name in names},
            "spm_units": {"spm_unit": {"members": names}},
            "families": {"family": {"members": names}},
            "marital_units": {
                f"marital_unit_{name}": {"members": [name]} for name in names
            },
            "households": {"household": {"members": names, "state_code": {year: "CA"}}},
        }
    )


def _enrollee(year, part_a, part_b, irmaa):
    return {
        "age": {year: 70},
        "is_medicare_eligible": {year: True},
        "medicare_enrolled": {year: True},
        "base_part_a_premium": {year: part_a},
        "gross_medicare_part_b_premium": {year: part_b},
        "income_adjusted_part_d_premium_surcharge": {year: irmaa},
    }


def _reference_medicare_cost(year, part_a, part_b, irmaa):
    date = f"{year}-01-01"
    gross = _read("calibration.gov.hhs.medicare.per_capita_cost", date) * _read(
        "calibration.gov.hhs.medicare.noninstitutionalized_spending_ratio", date
    )
    part_d = _share(year) * (_premium(year) + irmaa)
    return max(gross - part_a - part_b - part_d, 0)


premiums = st.floats(0, 40_000, allow_nan=False)
irmaas = st.floats(0, 12_000, allow_nan=False)


@settings(max_examples=25, deadline=None)
@given(years, st.floats(0, 12_000, allow_nan=False), premiums, irmaas, irmaas)
def test_medicare_cost_matches_reference_and_bounds(
    year, part_a, part_b, irmaa, more_irmaa
):
    low, high = sorted((irmaa, irmaa + more_irmaa))
    simulation = _simulation(
        year,
        {
            "low": _enrollee(year, part_a, part_b, low),
            "high": _enrollee(year, part_a, part_b, high),
        },
    )
    net = simulation.calculate("medicare_cost", year)
    gross = simulation.calculate("medicare_gross_cost", year)
    # Variables are float32, so compare to single precision.
    for value, surcharge in zip(net, (low, high)):
        expected = _reference_medicare_cost(year, part_a, part_b, surcharge)
        assert value == pytest.approx(expected, rel=1e-6, abs=0.01)
    assert (net >= 0).all()
    assert (net <= gross).all()
    # The gross cost subtracts no premium, so both people have the same one.
    assert gross[0] == gross[1]
    assert net[1] <= net[0]
