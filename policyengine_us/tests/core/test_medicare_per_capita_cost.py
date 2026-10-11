"""The CMS Medicare spending per enrollee series that values Medicare coverage.

``calibration.gov.hhs.medicare.per_capita_cost`` holds the "Medicare" row of
"Spending per Enrollee ($)" in CMS's National Health Expenditure projections,
Table 17 (2025-2034 release): Medicare spending over Medicare enrollment.
Spending covers every Part, including payments to Medicare Advantage plans and
program administration; enrollment counts Part A and/or Part B enrollees in
person-years; both exclude the territories (NHEA methodology paper, file pages
15, 23 and 34). 2013-2024 are historical and 2025-2034 projected, from the
projections prepared for the 2026 Medicare Trustees Report. 2035 to 2100 grow
at the 2031-2032 rate, because the end of sequestration on August 31, 2033
lifts 2033 and 2034 growth.

``medicare_gross_cost`` returns the series times
``noninstitutionalized_spending_ratio`` (enrollees outside nursing homes,
tested in test_medicare_noninstitutionalized_spending_ratio.py) for each
enrolled person, ``medicare_cost`` subtracts the person's Part A, gross Part
B and expected Part D premiums from that (tested in
test_medicare_cost_part_d_premium.py), and ``qmb_cost_sharing`` pays QMB
enrollees a share of it each month.

Invariants:

1. Transcription: every value is Table 17's published dollar figure, and is
   consistent with the same table's Medicare spending over Medicare enrollment
   within rounding.
2. Cross-source level: the Trustees Report's per beneficiary cost (Table V.D1)
   runs 5% to 8% above the series in every year from 2015 to 2034. V.D1 sums
   per-Part averages (its footnote 2), while Table II.B1 counts 63.4 million
   Part B and 56.8 million Part D enrollees among 69.3 million in 2025.
3. Bounds and order: the series is positive and strictly increasing from 2013
   to 2100, and holds the 2100 value afterwards.
4. Extension rule: each year from 2035 to 2100 equals the 2034 value times
   (26,552 / 25,185) ** (year - 2034), the closed form of the iterative
   extension; the 2035 value is within 0.1% of the 2034 value grown at the
   Trustees' 2034-2035 per beneficiary growth.
5. Calendar years: every date within a year reads the January 1 value.
6. Consumers: for an enrolled person, ``medicare_gross_cost`` equals the
   series times the noninstitutionalized ratio; ``medicare_cost`` equals that
   less the Part A premium, the gross Part B premium and the expected Part D
   premium, floored at zero, so never exceeds ``medicare_gross_cost``; a QMB
   enrollee's monthly ``qmb_cost_sharing`` is the scaled series over 12
   times the QMB rate. A person not enrolled gets zero.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system

SERIES = "calibration.gov.hhs.medicare.per_capita_cost"
RATIO = "calibration.gov.hhs.medicare.noninstitutionalized_spending_ratio"
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2013, 2034, 2100
YEARS = range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1)
GROWTH_YEARS = (2031, 2032)

# CMS NHE projections tables, Table 17, "Medicare" rows
# (https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70).
MEDICARE_SPENDING_PER_ENROLLEE = dict(
    zip(
        YEARS,
        (
            *(11_483, 11_683, 11_929, 12_119, 12_319, 12_795, 13_366, 13_547),
            *(14_293, 14_921, 15_915, 16_779, 17_751, 18_983, 20_096, 21_310),
            *(22_543, 23_789, 25_185, 26_552, 28_277, 30_129),
        ),
    )
)
MEDICARE_SPENDING_BILLIONS = dict(
    zip(
        YEARS,
        (
            *(588.9, 617.3, 647.7, 675.7, 704.9, 751.6, 805.2, 833.8, 894.6),
            *(951.7, 1037.3, 1118.0, 1204.0, 1314.6, 1422.7, 1544.2, 1664.6),
            *(1783.7, 1911.1, 2035.8, 2188.3, 2354.3),
        ),
    )
)
MEDICARE_ENROLLMENT_MILLIONS = dict(
    zip(
        YEARS,
        (
            *(51.3, 52.8, 54.3, 55.8, 57.2, 58.7, 60.2, 61.6, 62.6, 63.8),
            *(65.2, 66.6, 67.8, 69.2, 70.8, 72.5, 73.8, 75.0, 75.9, 76.7),
            *(77.4, 78.1),
        ),
    )
)
# 2026 Medicare Trustees Report, Table V.D1 (file page 210), "Total" average
# per beneficiary cost: historical through 2025, intermediate estimates after.
TRUSTEES_PER_BENEFICIARY_COST = dict(
    zip(
        range(2015, 2036),
        (
            *(12_734, 12_922, 13_127, 13_604, 14_224, 14_401, 15_170, 15_820),
            *(16_809, 17_837, 18_894, 20_430, 21_497, 22_783, 24_076, 25_401),
            *(26_826, 28_169, 29_989, 31_967, 33_687),
        ),
    )
)

years = st.integers(FIRST_YEAR, END_YEAR)


def _series(date):
    return get_parameter(system.parameters, SERIES)(date)


def _value(year):
    return _series(f"{year}-01-01")


def _scaled(year):
    return _value(year) * get_parameter(system.parameters, RATIO)(f"{year}-01-01")


@pytest.mark.parametrize("year", YEARS)
def test_series_is_table_17_medicare_spending_per_enrollee(year):
    assert _value(year) == MEDICARE_SPENDING_PER_ENROLLEE[year]


@pytest.mark.parametrize("year", YEARS)
def test_published_values_match_spending_over_enrollment(year):
    """Checks the transcribed rows against each other, so one mistyped
    spending, enrollment or per-enrollee figure fails."""
    spending = MEDICARE_SPENDING_BILLIONS[year]
    enrollment = MEDICARE_ENROLLMENT_MILLIONS[year]
    # Both components are rounded to one decimal and the published value to
    # the dollar.
    low = 1_000 * (spending - 0.05) / (enrollment + 0.05) - 0.5
    high = 1_000 * (spending + 0.05) / (enrollment - 0.05) + 0.5
    assert low <= MEDICARE_SPENDING_PER_ENROLLEE[year] <= high


@pytest.mark.parametrize("year", range(2015, LAST_PROJECTED_YEAR + 1))
def test_trustees_per_beneficiary_cost_runs_5_to_8_percent_above(year):
    ratio = TRUSTEES_PER_BENEFICIARY_COST[year] / _value(year)
    assert 1.05 <= ratio <= 1.08


def test_2035_extension_follows_the_trustees_2035_growth():
    trustees_growth = (
        TRUSTEES_PER_BENEFICIARY_COST[2035] / TRUSTEES_PER_BENEFICIARY_COST[2034]
    )
    assert _value(2035) == pytest.approx(
        _value(LAST_PROJECTED_YEAR) * trustees_growth, rel=0.001
    )


@given(years, st.integers(1, END_YEAR - FIRST_YEAR))
def test_series_is_positive_and_strictly_increasing(year, gap):
    later = min(year + gap, END_YEAR)
    if later == year:
        return
    assert 0 < _value(year) < _value(later)


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_extension_is_the_closed_form_of_the_2031_2032_growth(year):
    earlier, later = GROWTH_YEARS
    growth = (
        MEDICARE_SPENDING_PER_ENROLLEE[later]
        / (MEDICARE_SPENDING_PER_ENROLLEE[earlier])
    )
    expected = MEDICARE_SPENDING_PER_ENROLLEE[LAST_PROJECTED_YEAR] * growth ** (
        year - LAST_PROJECTED_YEAR
    )
    assert _value(year) == pytest.approx(expected, rel=1e-9)
    assert _value(year) / _value(year - 1) == pytest.approx(growth, rel=1e-12)


@given(st.integers(END_YEAR, END_YEAR + 100))
def test_series_holds_the_2100_value_afterwards(year):
    assert _value(year) == _value(END_YEAR)


@given(years, st.integers(1, 12), st.integers(1, 28))
def test_every_date_in_a_year_reads_the_january_value(year, month, day):
    assert _series(f"{year}-{month:02d}-{day:02d}") == _value(year)


def _person_simulation(year, person):
    members = ["person"]
    return Simulation(
        situation={
            "people": {"person": person},
            "tax_units": {"tax_unit": {"members": members}},
            "spm_units": {"spm_unit": {"members": members}},
            "families": {"family": {"members": members}},
            "marital_units": {"marital_unit": {"members": members}},
            "households": {
                "household": {"members": members, "state_code": {year: "CA"}}
            },
        }
    )


@settings(max_examples=20, deadline=None)
@given(
    st.integers(2015, END_YEAR),
    st.floats(0, 12_000, allow_nan=False),
    st.floats(0, 40_000, allow_nan=False),
)
def test_medicare_cost_nets_premiums_from_the_series(
    year, part_a_premium, part_b_premium
):
    simulation = _person_simulation(
        year,
        {
            "age": {year: 70},
            "is_medicare_eligible": {year: True},
            "medicare_enrolled": {year: True},
            "base_part_a_premium": {year: part_a_premium},
            "gross_medicare_part_b_premium": {year: part_b_premium},
            "income_adjusted_part_d_premium_surcharge": {year: 0},
        },
    )
    gross = simulation.calculate("medicare_gross_cost", year)[0]
    net = simulation.calculate("medicare_cost", year)[0]
    # Variables are float32, so compare to single precision.
    assert gross == pytest.approx(_scaled(year), rel=1e-6)
    part_d = system.parameters(f"{year}-01-01").calibration.gov.hhs.medicare.part_d
    part_d_premium = part_d.enrollment_share * part_d.premiums_per_enrollee
    expected = max(_scaled(year) - part_a_premium - part_b_premium - part_d_premium, 0)
    assert net == pytest.approx(expected, rel=1e-6, abs=0.01)
    assert net <= gross


@settings(max_examples=10, deadline=None)
@given(st.integers(2015, END_YEAR))
def test_person_not_enrolled_has_no_medicare_cost(year):
    simulation = _person_simulation(
        year,
        {
            "age": {year: 70},
            "is_medicare_eligible": {year: True},
            "medicare_enrolled": {year: False},
        },
    )
    assert simulation.calculate("medicare_gross_cost", year)[0] == 0
    assert simulation.calculate("medicare_cost", year)[0] == 0


@settings(max_examples=10, deadline=None)
@given(st.integers(2015, END_YEAR), st.integers(1, 12))
def test_qmb_cost_sharing_is_the_qmb_rate_of_monthly_spending(year, month):
    period = f"{year}-{month:02d}"
    rate = system.parameters(
        period
    ).gov.hhs.medicare.savings_programs.qmb.cost_sharing_rate
    simulation = _person_simulation(year, {"msp_category": {period: "QMB"}})
    assert simulation.calculate("qmb_cost_sharing", period)[0] == pytest.approx(
        _scaled(year) / 12 * rate, rel=1e-6
    )
