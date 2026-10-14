"""Cost-of-living indexing of the NYC income tax elimination credit thresholds.

Tax Law § 1310(h)(1)(B)(iii): for taxable years beginning on or after
January 1, 2026, the commissioner multiplies the statutory income thresholds
by one plus the cost-of-living adjustment, "the percentage by which the
consumer price index for the preceding calendar year exceeds the consumer
price index for calendar year two thousand twenty-four". Section
1310(h)(3)(A) makes a calendar year's index the average CPI-U for all urban
consumers over the twelve months ending August 31 of that year. The statute
prescribes no rounding.

The model computes the adjustment in
``parameters/uprating_extensions.py``
(``get_nyc_income_tax_elimination_credit_cola``) and projects the thresholds
from the statutory 2025 amounts
(``extend_nyc_income_tax_elimination_credit_thresholds``). These tests check:

(a) the 2026 thresholds on the live parameters against a factor computed here
    by hand from the 24 monthly CPI-U values in ``cpi_u.yaml``;
(b) the adjustment's window semantics on fixed synthetic series, plus
    property-based invariants;
(c) that every projected year scales the statutory amounts by one plus that
    year's adjustment, with one factor shared by every bracket and filing
    status, rather than chaining from the prior year;
(d) the Oregon Kids' Credit adjustment, which now shares the same window
    helper, at its tax year 2026 value.
"""

from fractions import Fraction
from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_core.parameters import Parameter, ParameterNode

from policyengine_us.parameters.uprating_extensions import (
    extend_nyc_income_tax_elimination_credit_thresholds,
    get_nyc_income_tax_elimination_credit_cola,
    get_or_ctc_cola,
)
from policyengine_us.system import system

NYC_CREDITS = system.parameters.gov.local.ny.nyc.tax.income.credits
THRESHOLDS = NYC_CREDITS.income_tax_elimination.income_threshold
CPI_U = system.parameters.gov.bls.cpi.cpi_u

# Statutory tax year 2025 thresholds keyed by number of dependents; the last
# entry in each table applies to that many dependents "or more".
# Tax Law § 1310(h)(1)(B)(i): joint filers and qualified surviving spouses.
JOINT_OR_SURVIVING_SPOUSE_THRESHOLDS = {
    1: 36_789,
    2: 46_350,
    3: 54_545,
    4: 61_071,
    5: 68_403,
    6: 75_204,
    7: 91_902,
}
# Tax Law § 1310(h)(1)(B)(ii): single, married filing separately and head of
# household filers.
SINGLE_SEPARATE_OR_HEAD_THRESHOLDS = {
    1: 31_503,
    2: 36_824,
    3: 46_512,
    4: 53_711,
    5: 59_928,
    6: 65_712,
    7: 74_565,
    8: 88_361,
}
STATUTORY_THRESHOLDS = {
    "joint": JOINT_OR_SURVIVING_SPOUSE_THRESHOLDS,
    "surviving_spouse": JOINT_OR_SURVIVING_SPOUSE_THRESHOLDS,
    "single": SINGLE_SEPARATE_OR_HEAD_THRESHOLDS,
    "separate": SINGLE_SEPARATE_OR_HEAD_THRESHOLDS,
    "head_of_household": SINGLE_SEPARATE_OR_HEAD_THRESHOLDS,
}

# Monthly CPI-U values transcribed by hand from
# parameters/gov/bls/cpi/cpi_u.yaml, independent of any model helper. If that
# series is revised, update these lists and FACTOR_2026 together.
# Calendar year 2024 index (§ 1310(h)(3)(A)): September 2023 - August 2024.
CPI_U_SEPTEMBER_2023_TO_AUGUST_2024 = (
    ("2023-09-01", "307.789"),
    ("2023-10-01", "307.671"),
    ("2023-11-01", "307.051"),
    ("2023-12-01", "306.746"),
    ("2024-01-01", "309.794"),
    ("2024-02-01", "311.022"),
    ("2024-03-01", "312.107"),
    ("2024-04-01", "313.016"),
    ("2024-05-01", "313.140"),
    ("2024-06-01", "313.131"),
    ("2024-07-01", "313.566"),
    ("2024-08-01", "314.131"),
)
# Calendar year 2025 index: September 2024 - August 2025.
CPI_U_SEPTEMBER_2024_TO_AUGUST_2025 = (
    ("2024-09-01", "314.851"),
    ("2024-10-01", "315.564"),
    ("2024-11-01", "316.449"),
    ("2024-12-01", "317.603"),
    ("2025-01-01", "319.086"),
    ("2025-02-01", "319.775"),
    ("2025-03-01", "319.615"),
    ("2025-04-01", "320.321"),
    ("2025-05-01", "320.580"),
    ("2025-06-01", "321.500"),
    ("2025-07-01", "322.132"),
    ("2025-08-01", "323.364"),
)
# The twelve values sum to 3,729.164 (average 310.7636...) for 2024 and
# 3,830.840 (average 319.2366...) for 2025. Both averages divide by 12, so the
# tax year 2026 factor is the ratio of the sums:
#   3,830.840 / 3,729.164 = 957,710 / 932,291 = 1.0272650921225...
# a cost-of-living adjustment of about 2.7265%.
FACTOR_2026 = Fraction(957_710, 932_291)
FACTOR_2026_DECIMAL = 1.0272650921225


def _twelve_month_sum(months):
    return sum(Fraction(value) for _, value in months)


def test_transcribed_cpi_u_values_match_the_parameter_file():
    for month, value in (
        CPI_U_SEPTEMBER_2023_TO_AUGUST_2024 + CPI_U_SEPTEMBER_2024_TO_AUGUST_2025
    ):
        assert CPI_U(month) == float(value), month


def test_hand_computed_2026_factor():
    sum_2024 = _twelve_month_sum(CPI_U_SEPTEMBER_2023_TO_AUGUST_2024)
    sum_2025 = _twelve_month_sum(CPI_U_SEPTEMBER_2024_TO_AUGUST_2025)
    assert sum_2024 == Fraction("3729.164")
    assert sum_2025 == Fraction("3830.840")
    assert (sum_2025 / 12) / (sum_2024 / 12) == FACTOR_2026
    assert float(FACTOR_2026) == pytest.approx(FACTOR_2026_DECIMAL, abs=1e-13)
    # The model's adjustment agrees with the hand computation.
    cola = get_nyc_income_tax_elimination_credit_cola(system.parameters, 2026)
    assert cola == pytest.approx(float(FACTOR_2026 - 1), rel=1e-12)


def _brackets(status):
    """Pair each bracket of a filing status with its statutory row."""
    scale = THRESHOLDS.children[status]
    statutory = STATUTORY_THRESHOLDS[status]
    assert len(scale.brackets) == len(statutory)
    return list(zip(scale.brackets, statutory.items()))


def test_every_filing_status_is_covered():
    assert set(THRESHOLDS.children) == set(STATUTORY_THRESHOLDS)


@pytest.mark.parametrize("status", sorted(STATUTORY_THRESHOLDS))
def test_2025_thresholds_are_the_statutory_amounts(status):
    for bracket, (dependents, amount) in _brackets(status):
        assert bracket.threshold("2025-01-01") == dependents
        assert bracket.amount("2025-01-01") == amount


@pytest.mark.parametrize("status", sorted(STATUTORY_THRESHOLDS))
def test_2026_thresholds_apply_the_hand_computed_factor(status):
    # The statute prescribes no rounding, so each threshold is the exact
    # product: $36,789 becomes $37,792.0555, not a whole-dollar amount.
    for bracket, (dependents, amount) in _brackets(status):
        expected = amount * FACTOR_2026
        assert expected.denominator != 1
        assert bracket.amount("2026-01-01") == pytest.approx(
            float(expected), rel=1e-12
        ), (status, dependents)
        # 2026 dependent keys are unchanged.
        assert bracket.threshold("2026-01-01") == dependents


# Synthetic CPI-U series for the adjustment's window semantics.


def _parameters_for_series(values):
    """A minimal parameter tree holding only a synthetic CPI-U series."""
    cpi_u = Parameter("cpi_u", data=dict(values))
    bls = SimpleNamespace(cpi=SimpleNamespace(cpi_u=cpi_u))
    return SimpleNamespace(gov=SimpleNamespace(bls=bls))


def _nyc_cola_on_series(values, tax_year):
    parameters = _parameters_for_series(values)
    return get_nyc_income_tax_elimination_credit_cola(parameters, tax_year)


def _monthly(values, start_year, start_month, end_year, end_month, level):
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        values[f"{year}-{month:02d}-01"] = level
        month += 1
        if month == 13:
            year, month = year + 1, 1


def _base_series():
    """Synthetic series shaped like the live one.

    The 2024 index window (September 2023 - August 2024) averages 300: six
    months at 294, then six at 306. The 2025 window (September 2024 - August
    2025) averages 324: six months at 318, then six at 330. August 2023 sits
    just before the 2024 window at 250, so a window shifted by a month lands
    elsewhere. Monthly observations end in August 2025; annual projection
    points follow at February instants.
    """
    values = {"2023-08-01": 250}
    _monthly(values, 2023, 9, 2024, 2, 294)
    _monthly(values, 2024, 3, 2024, 8, 306)
    _monthly(values, 2024, 9, 2025, 2, 318)
    _monthly(values, 2025, 3, 2025, 8, 330)
    values["2026-02-01"] = 339
    values["2027-02-01"] = 351
    return values


def test_cola_fully_observed_window_averages_monthly_data():
    # Tax year 2026 compares the 2025 index (324) with the 2024 index (300).
    # Windows shifted one month earlier would give 323 / 300 (window) or
    # 324 / 295.33 (base), so only September - August windows pass.
    assert _nyc_cola_on_series(_base_series(), 2026) == pytest.approx(24 / 300)
    # Tax year 2025 compares the 2024 index with itself.
    assert _nyc_cola_on_series(_base_series(), 2025) == 0


def test_cola_unobserved_window_uses_annual_projection_point():
    # The tax year 2027 window (September 2025 - August 2026) has no observed
    # month, so the February 2026 projection point (339) is the 2026 index.
    # Averaging the raw instants instead would give
    # (5 * 330 + 7 * 339) / 12 = 335.25.
    assert _nyc_cola_on_series(_base_series(), 2027) == pytest.approx(39 / 300)
    # Tax year 2028 reads the February 2027 projection point (351).
    assert _nyc_cola_on_series(_base_series(), 2028) == pytest.approx(51 / 300)


def test_cola_partial_window_carries_last_observation_flat():
    # A refresh adds September - December 2025 (330, 332, 334, 336) but not
    # yet February 2026, which still holds the 339 projection. The tax year
    # 2027 window averages the four observations with an eight-month tail at
    # the December level: (1,332 + 8 * 336) / 12 = 335. Averaging only the
    # observed months (333), reading the raw instants (336.75) or reading the
    # projection point (339) would each give a different answer.
    values = _base_series()
    values.update(
        {"2025-09-01": 330, "2025-10-01": 332, "2025-11-01": 334, "2025-12-01": 336}
    )
    assert _nyc_cola_on_series(values, 2027) == pytest.approx(35 / 300)
    # The completed tax year 2026 window and later unobserved windows are
    # unaffected.
    assert _nyc_cola_on_series(values, 2026) == pytest.approx(24 / 300)
    assert _nyc_cola_on_series(values, 2028) == pytest.approx(51 / 300)


def test_cola_partial_window_treats_an_observed_february_as_an_observation():
    # A refresh reaching June 2026 overwrites the February 2026 projection
    # (339) with an observation (342). The window averages five months at
    # 333, February at 342, March - June at 345 and a two-month tail at 345:
    # (1,665 + 342 + 1,380 + 690) / 12 = 339.75. Reading the February
    # instant as the year's projection would give 342.
    values = _base_series()
    _monthly(values, 2025, 9, 2026, 1, 333)
    values["2026-02-01"] = 342
    _monthly(values, 2026, 3, 2026, 6, 345)
    assert _nyc_cola_on_series(values, 2027) == pytest.approx(39.75 / 300)


def test_cola_floors_at_zero_when_the_index_falls_below_2024():
    # Deflation: the 2025 index (297) is below the 2024 index (300), so the
    # adjustment is zero rather than negative and thresholds cannot fall
    # below the statutory amounts.
    values = _base_series()
    _monthly(values, 2024, 9, 2025, 8, 297)
    assert _nyc_cola_on_series(values, 2026) == 0
    # A projection point below the 2024 index also floors at zero.
    values["2026-02-01"] = 288
    assert _nyc_cola_on_series(values, 2027) == 0
    # An index exactly equal to the 2024 index gives zero too.
    _monthly(values, 2024, 9, 2025, 8, 300)
    assert _nyc_cola_on_series(values, 2026) == 0


BASE_WINDOW_MONTHS = [(2023, month) for month in range(9, 13)] + [
    (2024, month) for month in range(1, 9)
]
WINDOW_2025_MONTHS = [(2024, month) for month in range(9, 13)] + [
    (2025, month) for month in range(1, 9)
]
CPI_LEVELS = st.floats(min_value=50, max_value=1_000)


@settings(max_examples=200, deadline=None, derandomize=True, database=None)
@given(
    base_window=st.lists(CPI_LEVELS, min_size=12, max_size=12),
    window_2025=st.lists(CPI_LEVELS, min_size=12, max_size=12),
    projections=st.lists(CPI_LEVELS, min_size=2, max_size=2),
    scale=st.floats(min_value=0.01, max_value=100),
)
def test_cola_invariants(base_window, window_2025, projections, scale):
    """Invariants for any CPI-U series observed through August 2025.

    1. The adjustment is the plain ratio of twelve-month averages (or of the
       projection point to the 2024 average) less one, floored at zero.
    2. It is never negative.
    3. It is unit-free: rescaling the whole series leaves it unchanged.
    """
    values = {}
    for (year, month), level in zip(
        BASE_WINDOW_MONTHS + WINDOW_2025_MONTHS, base_window + window_2025
    ):
        values[f"{year}-{month:02d}-01"] = level
    values["2026-02-01"], values["2027-02-01"] = projections
    index_2024 = sum(base_window) / 12
    expected = {
        2026: max(sum(window_2025) / 12 / index_2024 - 1, 0),
        2027: max(projections[0] / index_2024 - 1, 0),
        2028: max(projections[1] / index_2024 - 1, 0),
    }
    parameters = _parameters_for_series(values)
    scaled_parameters = _parameters_for_series(
        {instant: level * scale for instant, level in values.items()}
    )
    for tax_year, expected_cola in expected.items():
        cola = get_nyc_income_tax_elimination_credit_cola(parameters, tax_year)
        assert cola >= 0
        assert cola == pytest.approx(expected_cola, rel=1e-9, abs=1e-12)
        scaled_cola = get_nyc_income_tax_elimination_credit_cola(
            scaled_parameters, tax_year
        )
        assert scaled_cola == pytest.approx(cola, rel=1e-9, abs=1e-12)


# Projection on the live parameters: every year from the statutory base.

PROJECTED_YEARS = (2026, 2027, 2028, 2029, 2030, 2035, 2036, 2040, 2050, 2075, 2099)


@pytest.mark.parametrize("year", PROJECTED_YEARS + (2100,))
def test_projected_thresholds_scale_statutory_amounts_by_one_factor(year):
    """threshold(year) / statutory amount == 1 + COLA(year) for every bracket.

    Chaining from the prior year would compound the factors, and rounding
    would perturb brackets differently; either breaks this identity.
    """
    factor = 1 + get_nyc_income_tax_elimination_credit_cola(system.parameters, year)
    ratios = []
    for status in STATUTORY_THRESHOLDS:
        for bracket, (dependents, amount) in _brackets(status):
            ratio = bracket.amount(f"{year}-01-01") / amount
            assert ratio == pytest.approx(factor, rel=1e-12), (status, dependents)
            ratios.append(ratio)
    assert len(ratios) == 2 * 7 + 3 * 8
    assert max(ratios) - min(ratios) <= 1e-12 * factor


def test_thresholds_hold_their_last_projected_value_after_2100():
    for status in STATUTORY_THRESHOLDS:
        for bracket, _ in _brackets(status):
            assert bracket.amount("2150-01-01") == bracket.amount("2100-01-01")


# Projection on a synthetic parameter tree, exercising behaviour the live
# series cannot reach: deflation and a published value.


def _synthetic_threshold_parameters(cpi_values, published=None):
    """A tree holding a synthetic CPI-U series and the statutory thresholds.

    ``published`` maps (status, dependents) to {year: value} entries encoded
    after 2025, as a Department of Taxation and Finance publication would be.
    """
    published = published or {}
    data = {}
    for status, statutory in STATUTORY_THRESHOLDS.items():
        brackets = []
        for dependents, amount in statutory.items():
            amounts = {"2025-01-01": amount}
            for year, value in published.get((status, dependents), {}).items():
                amounts[f"{year}-01-01"] = value
            brackets.append(
                {"threshold": {"2025-01-01": dependents}, "amount": amounts}
            )
        data[status] = {
            "metadata": {
                "type": "single_amount",
                "threshold_unit": "dependent",
                "amount_unit": "currency-USD",
            },
            "brackets": brackets,
        }
    thresholds = ParameterNode("income_threshold", data=data)
    credits = SimpleNamespace(
        income_tax_elimination=SimpleNamespace(income_threshold=thresholds)
    )
    nyc = SimpleNamespace(tax=SimpleNamespace(income=SimpleNamespace(credits=credits)))
    gov = SimpleNamespace(
        bls=SimpleNamespace(cpi=SimpleNamespace(cpi_u=Parameter("cpi_u", cpi_values))),
        local=SimpleNamespace(ny=SimpleNamespace(nyc=nyc)),
    )
    return SimpleNamespace(gov=gov), thresholds


def _rising_then_falling_series():
    """2024 index 300; 2025 index 330; projections 360, 270, then 315."""
    values = {}
    _monthly(values, 2023, 9, 2024, 8, 300)
    _monthly(values, 2024, 9, 2025, 8, 330)
    values["2026-02-01"] = 360
    values["2027-02-01"] = 270
    values["2028-02-01"] = 315
    return values


def test_extension_recomputes_each_year_from_the_statutory_amounts():
    # Adjustments: 2026 +10%, 2027 +20%, 2028 floored at 0 (index 270 below
    # 300), 2029 +5%, and 2030 +5% (the last projection point persists).
    # Thresholds may fall from one year to the next, since each adjustment
    # measures against 2024 rather than the prior year, but never below the
    # statutory amounts.
    parameters, thresholds = _synthetic_threshold_parameters(
        _rising_then_falling_series()
    )
    extend_nyc_income_tax_elimination_credit_thresholds(parameters, end_year=2030)
    factors = {2025: 1, 2026: 1.1, 2027: 1.2, 2028: 1, 2029: 1.05, 2030: 1.05}
    for status, statutory in STATUTORY_THRESHOLDS.items():
        scale = thresholds.children[status]
        for bracket, amount in zip(scale.brackets, statutory.values()):
            for year, factor in factors.items():
                assert bracket.amount(f"{year}-01-01") == pytest.approx(
                    amount * factor, rel=1e-12
                ), (status, year)
            assert bracket.amount("2040-01-01") == bracket.amount("2030-01-01")


def test_extension_keeps_published_values_and_projects_after_them():
    # A published 2026 value for one bracket takes precedence for 2026; 2027
    # still applies its adjustment to the statutory amount, not to the
    # published value. Other brackets are projected from 2026 as usual.
    published = {("joint", 1): {2026: 40_000}}
    parameters, thresholds = _synthetic_threshold_parameters(
        _rising_then_falling_series(), published
    )
    extend_nyc_income_tax_elimination_credit_thresholds(parameters, end_year=2030)
    joint = thresholds.children["joint"].brackets
    assert joint[0].amount("2026-01-01") == 40_000
    assert joint[0].amount("2027-01-01") == pytest.approx(36_789 * 1.2, rel=1e-12)
    assert joint[1].amount("2026-01-01") == pytest.approx(46_350 * 1.1, rel=1e-12)


# Oregon Kids' Credit: the refactor moved its window average into the shared
# helper. test_or_ctc_sunset.py pins the 2026 dollar amounts, but those floor
# to $50 steps and cannot detect a small window change, so pin the adjustment.

# ORS 315.273(5)(c) base: CPI-U for the second quarter of 2022, transcribed by
# hand from parameters/gov/bls/cpi/cpi_u.yaml (sum 877.716, average 292.572).
CPI_U_2022_Q2 = (
    ("2022-04-01", "289.109"),
    ("2022-05-01", "292.296"),
    ("2022-06-01", "296.311"),
)


def test_or_ctc_2026_cola_uses_the_window_ending_august_2025():
    for month, value in CPI_U_2022_Q2:
        assert CPI_U(month) == float(value), month
    base = sum(Fraction(value) for _, value in CPI_U_2022_Q2) / 3
    assert base == Fraction("292.572")
    window = _twelve_month_sum(CPI_U_SEPTEMBER_2024_TO_AUGUST_2025) / 12
    # 319.2366... / 292.572 - 1 = 9.1139%.
    expected = window / base - 1
    assert float(expected) == pytest.approx(0.0911388194, abs=1e-10)
    assert get_or_ctc_cola(system.parameters, 2026) == pytest.approx(
        float(expected), rel=1e-12
    )
