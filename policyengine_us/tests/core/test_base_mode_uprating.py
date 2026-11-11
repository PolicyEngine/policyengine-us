"""Base-mode uprating of amounts that statutes index from a base year.

Core's base mode (``metadata.uprating.base``) projects each year after a
parameter's last stated value as

    base + round(base * (index(Y) / index(base.period) - 1))

with ``base.floor`` holding the index ratio at one or above, for statutes
that add "the percentage (if any) by which" the index exceeds its base-year
level. These tests check, on the shipped parameter tree:

(a) the invariants of every base-mode parameter in every projected year
    through 2100: a whole number of rounding steps above the base, never
    below the base, and never falling while its index rises;
(b) each projection against the formula recomputed here from the index;
(c) 26 U.S.C. 63(c)(2): the joint and surviving spouse standard deductions
    equal twice the single amount, and the separate amount the single
    amount, in every year;
(d) a back-test of the amounts the IRS printed against each statute's
    formula on the model's price series, with each departure pinned.

The tests for each program's own index (test_uprating_extensions.py,
test_hsa_contribution_limits.py,
test_nyc_income_tax_elimination_credit_indexing.py and test_or_ctc_sunset.py)
compare the projections with the cost-of-living helpers the retired
hand-coded extensions used.
"""

import math

import pytest
from policyengine_core.parameters import Parameter
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.parameters.uprating_extensions import (
    get_average_for_12_months_ending_august,
    get_irs_cola,
)
from policyengine_us.system import system

PARAMETERS = system.parameters
LAST_YEAR = 2100
SD = PARAMETERS.gov.irs.deductions.standard.amount
LTC = PARAMETERS.gov.irs.deductions.itemized.medical.long_term_care_premium_limit
CTC = PARAMETERS.gov.irs.credits.ctc


def _base_mode_parameters():
    return [
        parameter
        for parameter in PARAMETERS.get_descendants()
        if isinstance(parameter, Parameter)
        and isinstance(parameter.metadata.get("uprating"), dict)
        and "base" in parameter.metadata["uprating"]
    ]


BASE_MODE_PARAMETERS = _base_mode_parameters()
BASE_MODE_IDS = [parameter.name for parameter in BASE_MODE_PARAMETERS]

NYC_THRESHOLDS = "gov.local.ny.nyc.tax.income.credits.income_tax_elimination"


def test_base_mode_covers_the_statutory_amounts():
    names = set(BASE_MODE_IDS)
    expected = {
        "gov.irs.deductions.standard.amount.SINGLE",
        "gov.irs.deductions.standard.amount.SEPARATE",
        "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD",
        "gov.irs.credits.ctc.amount.base[0].amount",
        "gov.irs.credits.ctc.refundable.individual_max",
        "gov.irs.deductions.standard.dependent.amount",
        "gov.irs.deductions.standard.dependent.additional_earned_income",
        "gov.irs.ald.educator_expense.cap",
        "gov.irs.gross_income.health_savings_account_contributions.limit.self_only",
        "gov.irs.gross_income.health_savings_account_contributions.limit.family",
        "gov.states.or.tax.income.credits.ctc.amount",
        "gov.states.or.tax.income.credits.ctc.reduction.start",
        *(
            "gov.irs.deductions.itemized.medical.long_term_care_premium_limit"
            f"[{bracket}].amount"
            for bracket in range(5)
        ),
    }
    assert expected <= names, expected - names
    nyc = {name for name in names if name.startswith(NYC_THRESHOLDS)}
    # Two tables of 7 brackets and three of 8, amounts only.
    assert len(nyc) == 2 * 7 + 3 * 8
    assert all(name.endswith(".amount") for name in nyc)
    assert names == expected | nyc


def _spec(parameter):
    """Index, base period, base value, rounding and floor of a parameter."""
    meta = parameter.metadata["uprating"]
    base = meta["base"]
    period = base["period"]
    value = base.get("value")
    if value is None:
        value = parameter(f"{period}-01-01")
    index = get_parameter(PARAMETERS, meta["parameter"])
    return index, period, value, meta.get("rounding"), base.get("floor", False)


def _last_stated_year(parameter):
    return max(
        int(value.instant_str[:4])
        for value in parameter.values_list
        if value.file_path is not None
    )


def _projected_years(parameter):
    return range(_last_stated_year(parameter) + 1, LAST_YEAR + 1)


def _ratio(index, period, year, floor):
    ratio = index(f"{year}-01-01") / index(f"{period}-01-01")
    return max(ratio, 1) if floor else ratio


def _round_increase(increase, rounding):
    if rounding is None:
        return increase
    interval = rounding["interval"]
    # Absorb float error from the index ratio, as core's snap does.
    steps = round(increase / interval, 9)
    if rounding["type"] == "downwards":
        return math.floor(steps) * interval
    assert rounding["type"] == "nearest", rounding
    return round(steps) * interval


@pytest.mark.parametrize("parameter", BASE_MODE_PARAMETERS, ids=BASE_MODE_IDS)
def test_projections_keep_the_base_mode_invariants(parameter):
    index, period, base, rounding, floor = _spec(parameter)
    years = list(_projected_years(parameter))
    assert years, parameter.name
    previous_value = previous_index = None
    for year in years:
        value = parameter(f"{year}-01-01")
        if rounding is not None:
            steps = (value - base) / rounding["interval"]
            assert steps == pytest.approx(round(steps), abs=1e-9), year
        if floor:
            assert value >= base, year
        current_index = index(f"{year}-01-01")
        if previous_index is not None and current_index >= previous_index:
            assert value >= previous_value, year
        previous_value, previous_index = value, current_index
    # Projections hold their last value.
    assert parameter(f"{LAST_YEAR + 50}-01-01") == parameter(f"{LAST_YEAR}-01-01")


@pytest.mark.parametrize("parameter", BASE_MODE_PARAMETERS, ids=BASE_MODE_IDS)
def test_projections_match_the_formula_from_the_index(parameter):
    index, period, base, rounding, floor = _spec(parameter)
    for year in _projected_years(parameter):
        increase = base * (_ratio(index, period, year, floor) - 1)
        expected = base + _round_increase(increase, rounding)
        assert parameter(f"{year}-01-01") == pytest.approx(expected, rel=1e-12), year


def test_joint_standard_deduction_is_twice_the_single_amount_in_every_year():
    """63(c)(2)(A): 200% of the (C) amount; (C): half of (A) for separate
    returns; (B) and (C) index only the head of household and single
    amounts, 63(c)(7)(B)(ii)."""
    # 2015 is the first year amount.yaml states.
    for year in range(2015, LAST_YEAR + 1):
        period = f"{year}-01-01"
        single = SD.SINGLE(period)
        assert SD.JOINT(period) == 2 * single, year
        assert SD.SURVIVING_SPOUSE(period) == 2 * single, year
        assert SD.SEPARATE(period) == single, year


# Back-test: the printed amounts against the statute's formula, on the
# model's price series and the statute's own window (the C-CPI-U averaged
# over the 12 months ending August 31, 1(f)(4) and (6)), not
# gov.irs.uprating, whose window ends in July (#9105). A year whose window
# the series does not fully observe is skipped: the window helper carries
# the last observation flat, which the IRS never does.

CHAINED = PARAMETERS.gov.bls.cpi.c_cpi_u
CHAINED_MONTHS = {value.instant_str for value in CHAINED.values_list}
# February instants past the observations hold annual projection points.
LAST_OBSERVED_MONTH = max(
    instant for instant in CHAINED_MONTHS if not instant.endswith("-02-01")
)


def _window_observed(year):
    """Whether the series observes each month of the window for tax year
    ``year``: September of ``year - 2`` through August of ``year - 1``."""
    months = [f"{year - 2}-{month:02d}-01" for month in range(9, 13)] + [
        f"{year - 1}-{month:02d}-01" for month in range(1, 9)
    ]
    return all(
        month in CHAINED_MONTHS and month <= LAST_OBSERVED_MONTH for month in months
    )


def test_back_test_skips_only_the_unobserved_windows():
    """2026 reads Sep 2024-Aug 2025, all observed. c_cpi_u.yaml holds no
    October 2025 value and ends at June 2026, inside the 2027 window."""
    assert all(_window_observed(year) for year in range(2013, 2027))
    assert not _window_observed(2027)


def _statutory_cola(year, base_year):
    if base_year <= 2016:
        return get_irs_cola(PARAMETERS, year, base_year)
    numerator = get_average_for_12_months_ending_august(CHAINED, year - 1)
    denominator = get_average_for_12_months_ending_august(CHAINED, base_year)
    return max(numerator / denominator - 1, 0)


def _down(increase, interval):
    return math.floor(round(increase / interval, 9)) * interval


def _nearest(increase, interval):
    return round(round(increase / interval, 9)) * interval


# (label, parameter, base, base year, first year, last year, interval,
# rounding, {year: (printed, formula)} departures)
BACK_TESTS = [
    # 63(c)(7)(A)-(B) as TCJA enacted them: $12,000 and $18,000 from 2017.
    (
        "standard deduction single, TCJA",
        SD.SINGLE,
        12_000,
        2017,
        2018,
        2024,
        50,
        _down,
        {2022: (12_950, 12_900)},
    ),
    (
        "standard deduction head of household, TCJA",
        SD.HEAD_OF_HOUSEHOLD,
        18_000,
        2017,
        2018,
        2024,
        50,
        _down,
        {2020: (18_650, 18_600), 2021: (18_800, 18_850)},
    ),
    # As OBBBA amended them: $15,750 and $23,625 from 2024.
    (
        "standard deduction single",
        SD.SINGLE,
        15_750,
        2024,
        2025,
        2027,
        50,
        _down,
        {},
    ),
    (
        "standard deduction head of household",
        SD.HEAD_OF_HOUSEHOLD,
        23_625,
        2024,
        2025,
        2027,
        50,
        _down,
        # The printed 2026 increase, $525, is no multiple of $50.
        {2026: (24_150, 24_125)},
    ),
    # 24(i)(2): $2,200 from 2024; 24(h)(5) and (i)(1): $1,400 from 2017.
    (
        "child tax credit",
        CTC.amount.base.brackets[0].amount,
        2_200,
        2024,
        2025,
        2027,
        100,
        _down,
        {},
    ),
    (
        "child tax credit refundable maximum",
        CTC.refundable.individual_max,
        1_400,
        2017,
        2018,
        2027,
        100,
        _down,
        {},
    ),
    # 63(c)(4)(B): $500 from 1987 and $250 from 1997.
    (
        "dependent standard deduction floor",
        PARAMETERS.gov.irs.deductions.standard.dependent.amount,
        500,
        1987,
        2018,
        2027,
        50,
        _down,
        {},
    ),
    (
        "dependent standard deduction earned income addition",
        PARAMETERS.gov.irs.deductions.standard.dependent.additional_earned_income,
        250,
        1997,
        2013,
        2027,
        50,
        _down,
        {},
    ),
    # 62(d)(3): $250 from 2014, to the nearest $50.
    (
        "educator expense cap",
        PARAMETERS.gov.irs.ald.educator_expense.cap,
        250,
        2014,
        2016,
        2027,
        50,
        _nearest,
        {},
    ),
]


@pytest.mark.parametrize(
    "label, parameter, base, base_year, first, last, interval, rule, departures",
    BACK_TESTS,
    ids=[case[0] for case in BACK_TESTS],
)
def test_printed_amounts_against_the_statutory_formula(
    label, parameter, base, base_year, first, last, interval, rule, departures
):
    found = {}
    for year in range(first, last + 1):
        if not _window_observed(year):
            continue
        printed = parameter(f"{year}-01-01")
        formula = base + rule(base * _statutory_cola(year, base_year), interval)
        if printed != pytest.approx(formula, abs=1e-6):
            found[year] = (printed, formula)
    assert found == departures


# 213(d)(10)(B): the medical care index, with the components' August 2016
# ratio for the 1(f)(3)(B) amount, reproduces every 2027 limit in Rev. Proc.
# 2026-35 section 3.29; earlier printed limits depart by $5 to $30.
LTC_BASES = (200, 375, 750, 2_000, 2_500)
# The $375 limits the IRS printed before 2027 end in 0, where the $375 plus
# an increase rounded to $10 ends in 5.
LTC_DEPARTURES = {
    200: {},
    375: {
        2013: (680, 685),
        2014: (700, 695),
        2015: (710, 715),
        2016: (730, 735),
        2017: (770, 765),
        2018: (780, 775),
        2019: (790, 785),
        2020: (810, 815),
        2021: (850, 845),
        2022: (850, 845),
        2023: (890, 895),
        2024: (880, 875),
        2025: (900, 905),
        2026: (930, 935),
    },
    750: {2021: (1_690, 1_680), 2022: (1_690, 1_700), 2025: (1_800, 1_810)},
    2_000: {
        2018: (4_160, 4_150),
        2019: (4_220, 4_210),
        2020: (4_350, 4_340),
        2021: (4_520, 4_490),
        2022: (4_510, 4_530),
        2024: (4_710, 4_680),
        2025: (4_810, 4_820),
    },
    2_500: {
        2018: (5_200, 5_190),
        2019: (5_270, 5_260),
        2021: (5_640, 5_610),
        2022: (5_640, 5_660),
        2024: (5_880, 5_850),
    },
}


@pytest.mark.parametrize("bracket, base", list(enumerate(LTC_BASES)))
def test_printed_long_term_care_limits_against_the_statutory_formula(bracket, base):
    index = PARAMETERS.gov.irs.indexing.medical_care_c_cpi_u
    amount = LTC.brackets[bracket].amount
    found = {}
    for year in range(2013, 2028):
        printed = amount(f"{year}-01-01")
        ratio = index(f"{year}-01-01") / index("1997-01-01")
        formula = base + _nearest(base * (ratio - 1), 10)
        if printed != pytest.approx(formula, abs=1e-6):
            found[year] = (printed, formula)
    assert found == LTC_DEPARTURES[base]
    assert 2027 not in found
