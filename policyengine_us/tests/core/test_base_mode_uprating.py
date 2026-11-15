"""Base-mode uprating of amounts that statutes index from a base year.

Core's base mode (``metadata.uprating.base``) projects each year after a
parameter's last stated value as

    base + round(base * (index(Y) / index(base.period) - 1))

with ``base.floor`` holding the index ratio at one or above, for statutes
that add "the percentage (if any) by which" the index exceeds its base-year
level. These tests check, on the shipped parameter tree:

(a) the invariants of every base-mode parameter in every projected year
    through 2100: a whole number of rounding steps above the base, never
    below the base, and never falling while its index rises, from the last
    stated value on;
(b) each projection against the formula recomputed here from the index;
(c) each parameter's uprating metadata against a table read from the
    statute, and each projection against that table's constants, so a
    wrong base, base period or rounding rule in the metadata fails;
(d) 26 U.S.C. 63(c)(2): the joint and surviving spouse standard deductions
    equal twice the single amount, and the separate amount the single
    amount, in every year;
(e) a back-test of the amounts the IRS printed against each statute's
    formula on the model's price series, with each departure pinned.

The tests for each program's own index (test_uprating_extensions.py,
test_hsa_contribution_limits.py,
test_nyc_income_tax_elimination_credit_indexing.py and test_or_ctc_sunset.py)
compare the projections with the cost-of-living helpers the retired
hand-coded extensions used.
"""

import math
import numbers
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

import pytest
from hypothesis import given, settings, strategies as st
from policyengine_core.parameters import Parameter
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.parameters.operations.uprate_parameters import project_from_base

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
        "gov.states.az.tax.income.deductions.standard.amount.SINGLE",
        "gov.states.az.tax.income.deductions.standard.amount.SEPARATE",
        "gov.states.az.tax.income.deductions.standard.amount.HEAD_OF_HOUSEHOLD",
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


def _projection(base, index_at_year, index_at_base, rounding, floor):
    """One projection from recorded decimals; no snap or precision guessing."""
    if math.isinf(base):
        return float(base)
    if rounding is None:
        ratio = index_at_year / index_at_base
        return float(base * (max(ratio, 1.0) if floor else ratio))
    ratio = _exact(index_at_year) / _exact(index_at_base)
    if floor:
        ratio = max(ratio, Fraction(1))
    step = _exact(rounding["interval"])
    intervals = _exact(base) * (ratio - 1) / step
    whole, remainder = divmod(intervals.numerator, intervals.denominator)
    kind = rounding["type"]
    if kind == "upwards":
        whole += bool(remainder)
    elif kind == "nearest":
        whole += 2 * remainder >= intervals.denominator
    else:
        assert kind == "downwards", kind
    return float(_exact(base) + whole * step)


@pytest.mark.parametrize("parameter", BASE_MODE_PARAMETERS, ids=BASE_MODE_IDS)
def test_projections_keep_the_base_mode_invariants(parameter):
    index, period, base, rounding, floor = _spec(parameter)
    years = list(_projected_years(parameter))
    assert years, parameter.name
    # Start from the last stated year, so the step from the last IRS or CBO
    # value to the first projected value is checked too.
    last_stated = f"{_last_stated_year(parameter)}-01-01"
    previous_value, previous_index = parameter(last_stated), index(last_stated)
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
        expected = _projection(
            base, index(f"{year}-01-01"), index(f"{period}-01-01"), rounding, floor
        )
        actual = parameter(f"{year}-01-01")
        if rounding is None:
            assert actual == pytest.approx(expected, rel=1e-12), year
        else:
            assert actual == expected, year


# (c) The statute, read independently of the metadata. Each row gives the
# index, the base amount, the base period in the index's own periods, whether
# the statute floors the adjustment at zero ("the percentage (if any) by
# which"), and how it rounds the increase. Each index holds at period Y the
# price level of calendar year Y - 1 (for the medical care index, August of
# Y - 1; for Oregon's, period 2023 holds the second quarter of 2022), so a
# statute's base year B is period B + 1.


@dataclass(frozen=True)
class Statute:
    citation: str
    index: str
    # None: the base is the parameter's own value at the base period.
    base: Optional[float]
    period: int
    floor: bool
    # "downwards", "upwards" or "nearest"; None for no rounding.
    rounding: Optional[str]
    interval: Optional[int]


IRS_UPRATING = "gov.irs.uprating"
IRS_C_CPI_U = "gov.irs.indexing.c_cpi_u"
# 1(f)(3)(A): "the percentage (if any) by which" the C-CPI-U exceeds its
# base-year level, so every 1(f)(3) amount floors the adjustment.
SD_SINGLE = Statute(
    # 63(c)(7)(A)(ii) puts $15,750 in 63(c)(2)(C); (7)(B)(ii) indexes it with
    # 2024 as the base year, increases rounded to the next lowest $50.
    "26 U.S.C. 63(c)(7)(A)(ii), (B)(ii)",
    IRS_UPRATING,
    15_750,
    2025,
    True,
    "downwards",
    50,
)
LTC_INDEX = "gov.irs.indexing.medical_care_c_cpi_u"
LTC_CITATION = "26 U.S.C. 213(d)(10)(A), (B)"
NYC_INDEX = f"{NYC_THRESHOLDS}.cpi"
OR_INDEX = "gov.states.or.tax.income.credits.ctc.cpi"
AZ_SD = "gov.states.az.tax.income.deductions.standard.amount"
STATUTE = {
    "gov.irs.deductions.standard.amount.SINGLE": SD_SINGLE,
    # 63(c)(2)(C), "any other case", covers separate returns too.
    "gov.irs.deductions.standard.amount.SEPARATE": SD_SINGLE,
    "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": Statute(
        "26 U.S.C. 63(c)(7)(A)(i), (B)(ii)",
        IRS_UPRATING,
        23_625,
        2025,
        True,
        "downwards",
        50,
    ),
    # A.R.S. 43-1041(A) sets Arizona's amounts to the federal 2025 ones, and
    # 43-1041(H) indexes them "in the same manner in which the federal basic
    # standard deduction is adjusted for inflation pursuant to section 63".
    **{
        f"{AZ_SD}.{status}": Statute(
            "A.R.S. 43-1041(A), (H)",
            IRS_UPRATING,
            base,
            2025,
            True,
            "downwards",
            50,
        )
        for status, base in [
            ("SINGLE", 15_750),
            ("SEPARATE", 15_750),
            ("HEAD_OF_HOUSEHOLD", 23_625),
        ]
    },
    # 24(h)(2) $2,200; 24(i)(2) base year 2024; 24(i)(3) next lowest $100.
    "gov.irs.credits.ctc.amount.base[0].amount": Statute(
        "26 U.S.C. 24(h)(2), (i)(2)-(3)",
        IRS_UPRATING,
        2_200,
        2025,
        True,
        "downwards",
        100,
    ),
    # 24(h)(5)(A) $1,400; 24(i)(1) base year 2017; 24(i)(3) next lowest $100.
    "gov.irs.credits.ctc.refundable.individual_max": Statute(
        "26 U.S.C. 24(h)(5)(A), (i)(1), (i)(3)",
        IRS_UPRATING,
        1_400,
        2018,
        True,
        "downwards",
        100,
    ),
    # 213(d)(10)(A)'s 1997 amounts; (B)(ii) compares August of the preceding
    # year with August 1996, "the percentage (if any)"; (B)(i) rounds each
    # increase to the nearest $10.
    **{
        "gov.irs.deductions.itemized.medical.long_term_care_premium_limit"
        f"[{bracket}].amount": Statute(
            LTC_CITATION, LTC_INDEX, base, 1997, True, "nearest", 10
        )
        for bracket, base in enumerate((200, 375, 750, 2_000, 2_500))
    },
    # 63(c)(5)(A) $500 and (B) $250; 63(c)(4)(B)(i) base year 1987 and
    # (ii) 1997; 63(c)(4) rounds increases to the next lowest $50.
    "gov.irs.deductions.standard.dependent.amount": Statute(
        "26 U.S.C. 63(c)(4)(B)(i), (c)(5)(A)",
        IRS_C_CPI_U,
        500,
        1988,
        True,
        "downwards",
        50,
    ),
    "gov.irs.deductions.standard.dependent.additional_earned_income": Statute(
        "26 U.S.C. 63(c)(4)(B)(ii), (c)(5)(B)",
        IRS_C_CPI_U,
        250,
        1998,
        True,
        "downwards",
        50,
    ),
    # 62(a)(2)(D) $250; 62(d)(3) base year 2014, nearest $50.
    "gov.irs.ald.educator_expense.cap": Statute(
        "26 U.S.C. 62(a)(2)(D), (d)(3)",
        IRS_C_CPI_U,
        250,
        2015,
        True,
        "nearest",
        50,
    ),
    # 223(b)(2) $2,250 and $4,500; 223(g)(1) base year 1997 on 12 months
    # ending March 31; 223(g)(2) nearest $50.
    "gov.irs.gross_income.health_savings_account_contributions.limit.self_only": (
        Statute(
            "26 U.S.C. 223(b)(2)(A), (g)",
            "gov.irs.indexing.hsa_c_cpi_u",
            2_250,
            1998,
            True,
            "nearest",
            50,
        )
    ),
    "gov.irs.gross_income.health_savings_account_contributions.limit.family": (
        Statute(
            "26 U.S.C. 223(b)(2)(B), (g)",
            "gov.irs.indexing.hsa_c_cpi_u",
            4_500,
            1998,
            True,
            "nearest",
            50,
        )
    ),
    # ORS 315.273(3)(a) $1,000 and $25,000; (5)(b) "the percentage (if any)"
    # over the second quarter of 2022; (5)(d) next lower multiple of $50.
    "gov.states.or.tax.income.credits.ctc.amount": Statute(
        "ORS 315.273(3)(a), (5)", OR_INDEX, 1_000, 2023, True, "downwards", 50
    ),
    "gov.states.or.tax.income.credits.ctc.reduction.start": Statute(
        "ORS 315.273(3)(a), (5)", OR_INDEX, 25_000, 2023, True, "downwards", 50
    ),
}
# NY Tax Law 1310(h)(1)(B)(iii): each 2025 amount times one plus the
# percentage by which the CPI for the preceding year exceeds the 2024 CPI; no
# rounding. A CPI below its 2024 level exceeds it by no percentage, hence the
# floor. The 2025 amounts are the base.
NYC_STATUTE = Statute(
    "NY Tax Law 1310(h)(1)(B)(iii)", NYC_INDEX, None, 2025, True, None, None
)
# The joint and surviving spouse amounts are 200% of the 63(c)(2)(C) amount
# (63(c)(2)(A)), so they follow SINGLE; rounding to $100 only clears float
# error, since twice a multiple of $50 is a multiple of $100.
SD_FOLLOWER_UPRATING = {
    "parameter": "gov.irs.deductions.standard.amount.SINGLE",
    "rounding": {"type": "nearest", "interval": 100},
}


def _statute(name):
    if name.startswith(NYC_THRESHOLDS):
        return NYC_STATUTE
    return STATUTE[name]


def _metadata_spec(statute):
    """The uprating metadata block the statute implies."""
    base = {"period": statute.period}
    if statute.base is not None:
        base["value"] = statute.base
    if statute.floor:
        base["floor"] = True
    spec = {"parameter": statute.index, "base": base}
    if statute.rounding is not None:
        spec["rounding"] = {"type": statute.rounding, "interval": statute.interval}
    return spec


def test_the_statute_table_covers_every_base_mode_parameter():
    nyc = [name for name in BASE_MODE_IDS if name.startswith(NYC_THRESHOLDS)]
    assert set(BASE_MODE_IDS) == set(STATUTE) | set(nyc)


@pytest.mark.parametrize("parameter", BASE_MODE_PARAMETERS, ids=BASE_MODE_IDS)
def test_uprating_metadata_matches_the_statute(parameter):
    assert parameter.metadata["uprating"] == _metadata_spec(_statute(parameter.name))


@pytest.mark.parametrize("status", ["JOINT", "SURVIVING_SPOUSE"])
def test_joint_and_surviving_spouse_follow_the_single_amount(status):
    assert getattr(SD, status).metadata["uprating"] == SD_FOLLOWER_UPRATING


def _exact(value):
    if isinstance(value, numbers.Integral) and not isinstance(value, bool):
        return Fraction(int(value))
    return Fraction(repr(float(value)))


def _statutory_value(statute, base, year):
    """The single value required by the table's exact decimal rounding rule."""
    index = get_parameter(PARAMETERS, statute.index)
    rounding = (
        {"type": statute.rounding, "interval": statute.interval}
        if statute.rounding is not None
        else None
    )
    return _projection(
        base,
        index(f"{year}-01-01"),
        index(f"{statute.period}-01-01"),
        rounding,
        statute.floor,
    )


@pytest.mark.parametrize("parameter", BASE_MODE_PARAMETERS, ids=BASE_MODE_IDS)
def test_projections_follow_the_statute_table(parameter):
    """Every projected year from 2028 to 2100 against the table's constants
    and the index the table names. Stated IRS and CBO values come first:
    the CTC's run to 2035, the refundable maximum's to 2034."""
    statute = _statute(parameter.name)
    base = statute.base
    if base is None:
        base = parameter(f"{statute.period}-01-01")
    first = max(2028, _last_stated_year(parameter) + 1)
    for year in range(first, LAST_YEAR + 1):
        value = parameter(f"{year}-01-01")
        expected = _statutory_value(statute, base, year)
        if statute.rounding is None:
            assert value == pytest.approx(expected, rel=1e-12), year
        else:
            assert value == expected, (year, value, expected)


def test_joint_standard_deduction_is_twice_the_single_amount_in_every_year():
    """63(c)(2)(A): the joint and surviving spouse amount is 200% of the (C)
    amount; (C), "any other case", covers single and separate filers alike,
    so SEPARATE equals SINGLE. 63(c)(7)(B)(ii) indexes only the (B) and (C)
    amounts, for head of household and single filers."""
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
    """The 1(f)(3) adjustment for ``year`` as TCJA wrote it: the C-CPI-U
    over the base year's CPI-U times the 1(f)(3)(B) ratio.

    For tax years before 2018 the IRS divided the CPI-U by the CPI-U. The
    earned income addition and educator cap back-tests reach back to 2013
    and 2016, and recomputing those years with the CPI-U numerator gives the
    same rounded amounts ($350; $250), so the chained formula stands in for
    the older one there.
    """
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


def test_earned_income_addition_before_tcja_follows_the_cpi_u():
    """63(c)(5)(B)'s $250 under 63(c)(4)(B)(ii), before TCJA: 1(f)(3) then
    divided the CPI-U for the preceding calendar year by the CPI-U for 1997,
    each averaged over the 12 months ending August 31 (1(f)(4)). The amounts
    the IRS printed from 1998 ($250, $300 from 2006, $350 from 2013) match
    $250 plus that increase rounded down to $50 in every year, and agree
    with ``base.value`` at the 1998 base period."""
    addition = PARAMETERS.gov.irs.deductions.standard.dependent.additional_earned_income
    cpi_u = PARAMETERS.gov.bls.cpi.cpi_u
    base = get_average_for_12_months_ending_august(cpi_u, 1997)
    for year in range(1998, 2018):
        numerator = get_average_for_12_months_ending_august(cpi_u, year - 1)
        cola = max(numerator / base - 1, 0)
        assert addition(f"{year}-01-01") == 250 + _down(250 * cola, 50), year
    assert addition("1997-01-01") is None


# The model's medical August-2016 splice, a projection convention,
# reproduces every 2027 limit in Rev. Proc.
# 2026-35 section 3.29; earlier printed limits depart by $5 to $30.
# Section 1(f)(3)(B)'s default uses all-items averages over the 12 months
# ending August 2016.
# This back-test compares IRS amounts with the chosen model projection.
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
def test_printed_long_term_care_limits_against_the_model_projection(bracket, base):
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


@pytest.mark.parametrize(
    "base, index, interval, kind, expected",
    [
        (100, 1.0099999999995, 1, "downwards", 100),
        (100, 1.0100000000005, 1, "upwards", 102),
        (100, 1.01, 1, "downwards", 101),
        (100, 1.01, 1, "upwards", 101),
        (100, math.nextafter(1.005, 0), 1, "nearest", 100),
        (100, 1.005, 1, "nearest", 101),
        (100, math.nextafter(1.005, math.inf), 1, "nearest", 101),
        (100, 0.995, 1, "nearest", 100),
        (100, 0.985, 1, "nearest", 99),
        (375, 2.32, 10, "nearest", 875),
        (1400, 1.4, 10, "downwards", 1960),
    ],
)
def test_exact_projection_has_one_boundary_outcome(
    base, index, interval, kind, expected
):
    """Final core and independent oracle select the same single outcome."""
    rounding = {"interval": interval, "type": kind}
    assert _projection(base, index, 1, rounding, False) == expected
    assert project_from_base(base, index, 1, (interval, kind)) == expected


@pytest.mark.parametrize("floor", [False, True])
@pytest.mark.parametrize("base", [-math.inf, math.inf])
def test_projection_keeps_the_final_infinite_base_guard(base, floor):
    for rounding in (None, {"interval": 1, "type": "downwards"}):
        parsed = None if rounding is None else (1, "downwards")
        assert _projection(base, 1e-300, 1e300, rounding, floor) == base
        assert project_from_base(base, 1e-300, 1e300, parsed, floor) == base


@settings(max_examples=25, deadline=None)
@given(
    base=st.integers(min_value=1, max_value=10000),
    current=st.integers(min_value=1, max_value=20000),
    initial=st.integers(min_value=1, max_value=10000),
    interval=st.sampled_from([1, 10, 50, 100]),
    kind=st.sampled_from(["downwards", "upwards", "nearest"]),
    floor=st.booleans(),
)
def test_projection_oracle_agrees_and_adjacent_indices_are_monotone(
    base, current, initial, interval, kind, floor
):
    """Positive-base projections agree exactly and never fall as indices rise."""
    current /= 100
    initial /= 100
    indices = [math.nextafter(current, 0), current, math.nextafter(current, math.inf)]
    rounding = {"interval": interval, "type": kind}
    expected = [_projection(base, value, initial, rounding, floor) for value in indices]
    actual = [
        project_from_base(base, value, initial, (interval, kind), floor)
        for value in indices
    ]
    assert actual == expected
    assert actual == sorted(actual)
    if floor:
        assert all(value >= base for value in actual)
    for value in actual:
        assert (_exact(value) - _exact(base)) % _exact(interval) == 0
    # Unrounded projections retain the final engine's floating-point order.
    expected_unrounded = (
        base * max(current / initial, 1.0) if floor else base * (current / initial)
    )
    assert _projection(base, current, initial, None, floor) == expected_unrounded
    assert project_from_base(base, current, initial, None, floor) == expected_unrounded
