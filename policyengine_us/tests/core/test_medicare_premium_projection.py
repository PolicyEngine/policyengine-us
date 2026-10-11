"""Medicare premiums, deductible and IRMAA after CMS's last announced year.

CMS announces each year's Part A and B premiums, Part A deductible and
income-related monthly adjustment amounts (IRMAA) in the autumn before. For
later years the model projects them:

- The Part B standard premium and Part B IRMAA amounts uprate by the
  Medicare Trustees' projected standard premium, rounded to 10 cents.
- The Part A premiums and deductible uprate by the Trustees' projections,
  rounded to $1 and $4.
- The IRMAA income thresholds follow 42 U.S.C. 1395r(i)(5)'s CPI-U schedule.
- The Part D IRMAA amounts apply 42 U.S.C. 1395w-113(a)(7)(B) to the
  Trustees' projected base beneficiary premium.

These tests read the parameter tree, plus one small parameter tree built for
the precedence tests. Household calculations are in the YAML tests under
``tests/policy/baseline/gov/hhs/medicare``.

Invariants:

1. Source agreement (differential, model against published figures): for
   2027-2035, the projections equal the 2026 Trustees Report's Part B
   premium (Table V.E2), Part A premiums and deductible (Table V.E1) and
   Part D IRMAA amounts (Table V.E4). The Part B IRMAA amounts are within
   $0.30 of Table V.E3 through 2034 and $0.80 in 2035, where Table V.E3
   implies a $360.90 standard premium against Table V.E2's $360.60.
2. Statutory rounding: in every projected year, the Part B premium and IRMAA
   amounts are multiples of 10 cents, the Part A premiums of $1 and the
   deductible of $4.
3. Agreement with the uprater: the Part B premium equals the Trustees series
   rounded to 10 cents in every year from 2021.
4. Proportionality: each Part B IRMAA amount stays at its 42 U.S.C.
   1395r(i)(3)(A) multiple of the standard premium, to within 0.1% plus
   rounding, as in CMS's 2026 amounts. Each Part D amount equals
   1395w-113(a)(7)(B) applied to the base beneficiary premium. The reduced
   Part A premium stays at 55% of the full premium (1395i-2(d)(4)), to
   within 0.1% plus $1. CMS rounded 2026's $310.75 to $311, and uprating
   from 2026 keeps that 0.04% excess, as it keeps the IRMAA amounts'.
5. Monotonicity: the Part B premium rises every year from 2023, and the Part
   A premiums and deductible never fall from 2024. IRMAA thresholds never
   fall from one year to the next and rise from tier to tier. Intended
   exception: the married-filing-separately top threshold is $500,000 less
   the rising unmarried threshold, so it falls each year until the $500,000
   amount is indexed in 2028.
6. Threshold structure: joint thresholds are twice the unmarried amounts
   (150% for the top tier), married filing separately uses the unmarried
   threshold and the top amount less that threshold, and Part D uses the Part
   B thresholds. The top tier stays at $500,000 through 2027.
7. Indexing (differential): the statutory CPI-U schedule reproduces CMS's
   published thresholds exactly for 2020-2024, where the model's CPI-U is
   the published not seasonally adjusted index, and within one $1,000 step
   for 2025-2026, where it is seasonally adjusted.
8. Precedence: a CMS amount added to the YAML for a year replaces the
   projection for that year only; later years are still computed from the
   statute rather than chained from it.
9. Extension: the new Trustees series grow at their last one-year rate past
   2035 and hold their 2100 value after 2100.
"""

from types import SimpleNamespace

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.parameters.uprating_extensions import (
    MEDICARE_IRMAA_APPLICABLE_PERCENTAGES,
    MEDICARE_IRMAA_TOP_FIRST_INDEXED_YEAR,
    extend_medicare_irmaa_thresholds,
    extend_medicare_part_d_irmaa_amounts,
    get_medicare_irmaa_thresholds,
    get_medicare_irmaa_unmarried_amounts,
    get_medicare_part_d_irmaa_amount,
)
from policyengine_us.system import system

PARAMETERS = system.parameters
MEDICARE = PARAMETERS.gov.hhs.medicare
CMS = "calibration.gov.hhs.cms"
PART_B_SERIES = f"{CMS}.medicare_part_b_premium_per_enrollee"
PART_A_SERIES = f"{CMS}.medicare_part_a_premium_per_enrollee"
DEDUCTIBLE_SERIES = f"{CMS}.medicare_part_a_deductible"
PART_D_SERIES = f"{CMS}.medicare_part_d_base_beneficiary_premium_per_enrollee"
LAST_ANNOUNCED_YEAR = 2026
LAST_TRUSTEES_YEAR = 2035
END_YEAR = 2100
FILING_STATUSES = ("single", "joint", "head_of_household", "surviving_spouse")
ALL_STATUSES = (*FILING_STATUSES, "separate")
PROJECTED_YEARS = st.integers(LAST_ANNOUNCED_YEAR + 1, END_YEAR + 20)
TRUSTEES_YEARS = range(LAST_ANNOUNCED_YEAR + 1, LAST_TRUSTEES_YEAR + 1)


def _at(parameter, year):
    return parameter(f"{year}-01-01")


def _series(path, year):
    return _at(get_parameter(PARAMETERS, path), year)


def _is_multiple(value, step):
    return abs(value / step - round(value / step)) < 1e-6


# 2026 Medicare Trustees Report (transmitted 2026-06-09, sha256
# ffa56b91...8fa8), intermediate estimates for 2027-2035.
# Table V.E1 (file page 212): inpatient hospital deductible, standard and
# reduced monthly Part A premiums.
TRUSTEES_PART_A_DEDUCTIBLE = dict(
    zip(
        range(2026, 2036),
        (1_736, 1_788, 1_844, 1_900, 1_960, 2_028, 2_092, 2_160, 2_228, 2_296),
    )
)
TRUSTEES_PART_A_FULL_PREMIUM = dict(
    zip(TRUSTEES_YEARS, (600, 629, 660, 694, 730, 767, 812, 862, 900))
)
TRUSTEES_PART_A_REDUCED_PREMIUM = dict(
    zip(TRUSTEES_YEARS, (330, 346, 363, 382, 402, 422, 447, 474, 495))
)
# Table V.E2 (file page 213): standard monthly Part B premium and Part D base
# beneficiary premium.
TRUSTEES_PART_B_PREMIUM = dict(
    zip(
        TRUSTEES_YEARS,
        (209.5, 224.5, 238.5, 255.5, 272.1, 290.2, 313.6, 338.5, 360.6),
    )
)
TRUSTEES_PART_D_BASE_PREMIUM = dict(
    zip(
        TRUSTEES_YEARS,
        (41.33, 43.81, 46.44, 68.93, 71.27, 71.59, 74.01, 75.48, 77.81),
    )
)
# Table V.E3 (file page 215): Part B income-related monthly adjustment
# amounts for the 35, 50, 65, 80 and 85 percent tiers.
TRUSTEES_PART_B_IRMAA = {
    2027: (83.70, 209.40, 335.10, 460.70, 502.60),
    2028: (89.80, 224.50, 359.20, 493.90, 538.80),
    2029: (95.30, 238.40, 381.50, 524.50, 572.20),
    2030: (102.10, 255.40, 408.70, 561.90, 613.00),
    2031: (108.80, 272.10, 435.40, 598.60, 653.00),
    2032: (116.00, 290.10, 464.20, 638.30, 696.30),
    2033: (125.40, 313.60, 501.80, 689.90, 752.60),
    2034: (135.30, 338.40, 541.50, 744.50, 812.20),
    2035: (144.40, 360.90, 577.40, 794.00, 866.20),
}
# Table V.E4 (file page 218): Part D income-related monthly adjustment
# amounts for the same tiers.
TRUSTEES_PART_D_IRMAA = {
    2027: (15.40, 39.70, 64.00, 88.30, 96.40),
    2028: (16.30, 42.10, 67.90, 93.60, 102.20),
    2029: (17.30, 44.60, 71.90, 99.30, 108.40),
    2030: (51.70, 103.40, 155.10, 206.80, 224.00),
    2031: (53.50, 106.90, 160.40, 213.80, 231.60),
    2032: (53.70, 107.40, 161.10, 214.80, 232.70),
    2033: (55.50, 111.00, 166.50, 222.00, 240.50),
    2034: (56.60, 113.20, 169.80, 226.40, 245.30),
    2035: (58.40, 116.70, 175.10, 233.40, 252.90),
}
# 42 U.S.C. 1395r(i)(3)(A): (applicable percentage - 25 points) x 200% of the
# aged actuarial rate, which is 4 x (applicable percentage - 25 points) times
# the standard premium of 50% of that rate.
PART_B_IRMAA_MULTIPLES = (0.4, 1.0, 1.6, 2.2, 2.4)
# CMS fact sheets "2020/2021/2022/2023 Medicare Parts A & B Premiums and
# Deductibles": the unmarried amounts above which the 35, 50, 65 and 80
# percent tiers begin. 2024-2026 are the YAML's published values.
CMS_UNMARRIED_AMOUNTS = {
    2020: (87_000, 109_000, 136_000, 163_000),
    2021: (88_000, 111_000, 138_000, 165_000),
    2022: (91_000, 114_000, 142_000, 170_000),
    2023: (97_000, 123_000, 153_000, 183_000),
    2024: (103_000, 129_000, 161_000, 193_000),
    2025: (106_000, 133_000, 167_000, 200_000),
    2026: (109_000, 137_000, 171_000, 205_000),
}


def _brackets(program, status):
    return getattr(program.irmaa, status).brackets


def _thresholds(program, status, year):
    return [_at(b.threshold, year) for b in _brackets(program, status)]


# 1. Source agreement.


@pytest.mark.parametrize("year", TRUSTEES_YEARS)
def test_part_b_premium_is_the_trustees_projection(year):
    assert _at(MEDICARE.part_b.base_premium, year) == pytest.approx(
        TRUSTEES_PART_B_PREMIUM[year], abs=1e-9
    )


@pytest.mark.parametrize("year", TRUSTEES_YEARS)
def test_part_a_premiums_are_the_trustees_projection(year):
    assert _at(MEDICARE.part_a.full_premium, year) == pytest.approx(
        TRUSTEES_PART_A_FULL_PREMIUM[year], abs=1e-9
    )
    assert _at(MEDICARE.part_a.reduced_premium, year) == pytest.approx(
        TRUSTEES_PART_A_REDUCED_PREMIUM[year], abs=1e-9
    )


@pytest.mark.parametrize("year", sorted(TRUSTEES_PART_A_DEDUCTIBLE))
def test_part_a_deductible_is_the_trustees_figure(year):
    """2026 is CMS's announced $1,736; later years are projections."""
    assert _at(MEDICARE.part_a.deductible, year) == pytest.approx(
        TRUSTEES_PART_A_DEDUCTIBLE[year], abs=1e-9
    )


@pytest.mark.parametrize("year", TRUSTEES_YEARS)
@pytest.mark.parametrize("status", FILING_STATUSES)
def test_part_b_irmaa_is_within_cents_of_the_trustees_projection(status, year):
    tolerance = (0.80 if year == LAST_TRUSTEES_YEAR else 0.30) + 1e-9
    amounts = [_at(b.amount, year) for b in _brackets(MEDICARE.part_b, status)[1:]]
    assert amounts == pytest.approx(TRUSTEES_PART_B_IRMAA[year], abs=tolerance)


@pytest.mark.parametrize("year", TRUSTEES_YEARS)
@pytest.mark.parametrize("status", FILING_STATUSES)
def test_part_d_irmaa_is_the_trustees_projection(status, year):
    """Applying the statute to the Trustees' base beneficiary premium, with
    the 20 percent base from 2030, reproduces their Table V.E4."""
    amounts = [_at(b.amount, year) for b in _brackets(MEDICARE.part_d, status)[1:]]
    assert amounts == pytest.approx(TRUSTEES_PART_D_IRMAA[year], abs=1e-9)


@pytest.mark.parametrize("year", TRUSTEES_YEARS)
def test_married_filing_separately_gets_the_two_top_tiers(year):
    for program in (MEDICARE.part_b, MEDICARE.part_d):
        separate = [_at(b.amount, year) for b in _brackets(program, "separate")]
        single = [_at(b.amount, year) for b in _brackets(program, "single")]
        assert separate == [0, *single[-2:]]


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_part_d_formula_reproduces_cms_published_amounts(year):
    """Differential check of the formula and its rounding against CMS's
    published amounts, from CMS's published base beneficiary premiums."""
    base_premium = _series(PART_D_SERIES, year)
    for status in ALL_STATUSES:
        brackets = _brackets(MEDICARE.part_d, status)[1:]
        for bracket, percentage in zip(
            brackets, MEDICARE_IRMAA_APPLICABLE_PERCENTAGES[status]
        ):
            assert get_medicare_part_d_irmaa_amount(
                base_premium, percentage, 0.255
            ) == pytest.approx(_at(bracket.amount, year), abs=1e-9)


@pytest.mark.parametrize(
    "path, values",
    [
        (PART_A_SERIES, TRUSTEES_PART_A_FULL_PREMIUM),
        (DEDUCTIBLE_SERIES, TRUSTEES_PART_A_DEDUCTIBLE),
        (PART_D_SERIES, TRUSTEES_PART_D_BASE_PREMIUM),
    ],
)
def test_new_series_transcribe_the_trustees_tables(path, values):
    for year, value in values.items():
        assert _series(path, year) == value


@pytest.mark.parametrize("year", range(2021, LAST_ANNOUNCED_YEAR + 1))
def test_part_a_series_agrees_with_announced_premiums(year):
    assert _series(PART_A_SERIES, year) == _at(MEDICARE.part_a.full_premium, year)


@pytest.mark.parametrize("year", range(2024, LAST_ANNOUNCED_YEAR + 1))
def test_deductible_series_agrees_with_announced_deductibles(year):
    assert _series(DEDUCTIBLE_SERIES, year) == _at(MEDICARE.part_a.deductible, year)


# 2. Statutory rounding.


@given(PROJECTED_YEARS)
def test_projected_amounts_are_rounded_as_published(year):
    assert _is_multiple(_at(MEDICARE.part_b.base_premium, year), 0.1)
    assert _is_multiple(_at(MEDICARE.part_a.full_premium, year), 1)
    assert _is_multiple(_at(MEDICARE.part_a.reduced_premium, year), 1)
    assert _is_multiple(_at(MEDICARE.part_a.deductible, year), 4)
    for program in (MEDICARE.part_b, MEDICARE.part_d):
        for status in ALL_STATUSES:
            for bracket in _brackets(program, status):
                assert _is_multiple(_at(bracket.amount, year), 0.1)


# 3. Agreement with the uprater.


@given(st.integers(2021, END_YEAR + 20))
def test_part_b_premium_is_the_series_rounded_to_ten_cents(year):
    series = _series(PART_B_SERIES, year)
    premium = _at(MEDICARE.part_b.base_premium, year)
    assert premium == pytest.approx(round(series / 0.1) * 0.1, abs=1e-9)
    assert abs(premium - series) <= 0.05 + 1e-9


# 4. Proportionality.


@given(PROJECTED_YEARS, st.sampled_from(FILING_STATUSES))
def test_part_b_irmaa_keeps_its_statutory_multiple(year, status):
    premium = _at(MEDICARE.part_b.base_premium, year)
    for bracket, multiple in zip(
        _brackets(MEDICARE.part_b, status)[1:], PART_B_IRMAA_MULTIPLES
    ):
        expected = multiple * premium
        assert abs(_at(bracket.amount, year) - expected) <= 0.001 * expected + 0.1


@given(PROJECTED_YEARS, st.sampled_from(ALL_STATUSES))
def test_part_d_irmaa_follows_the_statute(year, status):
    base_premium = _series(PART_D_SERIES, year)
    base_percent = _at(MEDICARE.part_d.base_beneficiary_premium_percent, year)
    for bracket, percentage in zip(
        _brackets(MEDICARE.part_d, status)[1:],
        MEDICARE_IRMAA_APPLICABLE_PERCENTAGES[status],
    ):
        assert _at(bracket.amount, year) == get_medicare_part_d_irmaa_amount(
            base_premium, percentage, base_percent
        )


def test_part_d_base_percent_resets_in_2030():
    percent = MEDICARE.part_d.base_beneficiary_premium_percent
    assert _at(percent, 2029) == 0.255
    assert _at(percent, 2030) == 0.2


@given(st.integers(2024, END_YEAR + 20))
def test_reduced_part_a_premium_is_55_percent_of_the_full_premium(year):
    expected = 0.55 * _at(MEDICARE.part_a.full_premium, year)
    reduced = _at(MEDICARE.part_a.reduced_premium, year)
    assert abs(reduced - expected) <= 0.001 * expected + 1


# 5. Monotonicity.


@given(st.integers(2023, END_YEAR - 1), st.integers(1, 80))
def test_part_b_premium_rises_every_year_from_2023(year, gap):
    later = min(year + gap, END_YEAR)
    assert _at(MEDICARE.part_b.base_premium, year) < _at(
        MEDICARE.part_b.base_premium, later
    )


@given(st.integers(2024, END_YEAR + 20), st.integers(1, 80))
def test_part_a_amounts_never_fall_from_2024(year, gap):
    for parameter in (
        MEDICARE.part_a.full_premium,
        MEDICARE.part_a.reduced_premium,
        MEDICARE.part_a.deductible,
    ):
        assert _at(parameter, year) <= _at(parameter, year + gap)


@given(st.integers(2024, END_YEAR + 20), st.integers(1, 80))
def test_irmaa_thresholds_never_fall(year, gap):
    for program in (MEDICARE.part_b, MEDICARE.part_d):
        for status in ALL_STATUSES:
            brackets = _brackets(program, status)
            for bracket in brackets:
                if (
                    status == "separate"
                    and bracket is brackets[-1]
                    and year < MEDICARE_IRMAA_TOP_FIRST_INDEXED_YEAR
                ):
                    continue  # The intended exception; see the next test.
                assert _at(bracket.threshold, year) <= _at(
                    bracket.threshold, year + gap
                )


@pytest.mark.parametrize("year", range(2025, MEDICARE_IRMAA_TOP_FIRST_INDEXED_YEAR))
def test_separate_top_threshold_falls_until_2028(year):
    """$500,000 less the unmarried threshold: $397,000 in 2024, $394,000 in
    2025 and $391,000 in 2026 as CMS published, then lower until 2028."""
    top = _brackets(MEDICARE.part_b, "separate")[-1].threshold
    assert _at(top, year) < _at(top, year - 1)
    single = _thresholds(MEDICARE.part_b, "single", year)
    assert _at(top, year) == 500_000 - (single[1] - 1)


@given(st.integers(2024, END_YEAR + 20))
def test_irmaa_tiers_rise_with_income_and_amount(year):
    for program in (MEDICARE.part_b, MEDICARE.part_d):
        for status in ALL_STATUSES:
            brackets = _brackets(program, status)
            thresholds = [_at(b.threshold, year) for b in brackets]
            amounts = [_at(b.amount, year) for b in brackets]
            assert thresholds == sorted(set(thresholds))
            assert amounts == sorted(set(amounts))


# 6. Threshold structure.


@given(st.integers(2024, END_YEAR + 20))
def test_thresholds_follow_the_filing_status_rules(year):
    single = _thresholds(MEDICARE.part_b, "single", year)
    lower, top = [t - 1 for t in single[1:5]], single[5]
    assert _thresholds(MEDICARE.part_b, "head_of_household", year) == single
    assert _thresholds(MEDICARE.part_b, "surviving_spouse", year) == single
    assert _thresholds(MEDICARE.part_b, "joint", year) == [
        0,
        *(2 * amount + 1 for amount in lower),
        1.5 * top,
    ]
    assert _thresholds(MEDICARE.part_b, "separate", year) == [
        0,
        lower[0] + 1,
        top - lower[0],
    ]
    for status in ALL_STATUSES:
        assert _thresholds(MEDICARE.part_d, status, year) == _thresholds(
            MEDICARE.part_b, status, year
        )


@given(st.integers(2024, END_YEAR + 20))
def test_unmarried_amounts_are_whole_thousands(year):
    """The first four thresholds sit $1 above a $1,000 multiple ("more
    than" the amount); the top tier starts at a $1,000 multiple."""
    single = _thresholds(MEDICARE.part_b, "single", year)
    assert all(_is_multiple(t - 1, 1_000) for t in single[1:5])
    assert _is_multiple(single[5], 1_000)


@pytest.mark.parametrize("year", range(2024, 2028))
def test_top_tier_is_not_indexed_before_2028(year):
    assert _thresholds(MEDICARE.part_b, "single", year)[5] == 500_000
    assert _thresholds(MEDICARE.part_b, "joint", year)[5] == 750_000


def test_top_tier_is_indexed_from_2028():
    assert _thresholds(MEDICARE.part_b, "single", 2028)[5] > 500_000


@pytest.mark.parametrize("year", range(2024, LAST_ANNOUNCED_YEAR + 1))
def test_threshold_rules_reproduce_the_published_scales(year):
    """Rebuilding each published year's scales from its unmarried amounts
    reproduces every filing status's published thresholds."""
    lower = tuple(float(a) for a in CMS_UNMARRIED_AMOUNTS[year])
    rebuilt = get_medicare_irmaa_thresholds(lower, 500_000.0)
    for status in ALL_STATUSES:
        assert _thresholds(MEDICARE.part_b, status, year) == list(rebuilt[status])


# 7. Indexing against CMS's published thresholds.


@pytest.mark.parametrize("year", sorted(CMS_UNMARRIED_AMOUNTS))
def test_cpi_schedule_reproduces_published_thresholds(year):
    lower, top = get_medicare_irmaa_unmarried_amounts(PARAMETERS, year)
    published = CMS_UNMARRIED_AMOUNTS[year]
    assert top == 500_000
    if year <= 2024:
        assert lower == published
    else:
        # From January 2024 the model's CPI-U is seasonally adjusted, while
        # CMS averages the published index; 2025's 12-month averages differ
        # by about 0.05%, enough to move two amounts one rounding step.
        assert all(abs(a - b) <= 1_000 for a, b in zip(lower, published))


def test_cpi_schedule_starts_in_2020():
    with pytest.raises(ValueError):
        get_medicare_irmaa_unmarried_amounts(PARAMETERS, 2019)


# 8. Precedence of published amounts.


def _medicare_tree_with_2027_values():
    """The IRMAA scales as loaded from YAML, with a 2027 value added to each
    bracket, under a root that shares the system's CPI-U and Trustees
    series."""
    data = {}
    for program in ("part_b", "part_d"):
        node = getattr(MEDICARE, program).irmaa
        data[program] = {"irmaa": {}}
        for status, scale in node.children.items():
            brackets = []
            for index, bracket in enumerate(scale.brackets):
                entry = {}
                for field in ("threshold", "amount"):
                    parameter = getattr(bracket, field)
                    values = {
                        v.instant_str: v.value
                        for v in parameter.values_list
                        if v.instant_str <= f"{LAST_ANNOUNCED_YEAR}-12-31"
                    }
                    # A stand-in for a CMS announcement: last year's value
                    # plus $1, which no projection produces. The first tier
                    # pays no adjustment in any year.
                    if field == "threshold" or index > 0:
                        last = values[f"{LAST_ANNOUNCED_YEAR}-01-01"]
                        values["2027-01-01"] = last + 1
                    entry[field] = {"values": values}
                brackets.append(entry)
            data[program]["irmaa"][status] = {
                "metadata": {"type": "single_amount"},
                "brackets": brackets,
            }
    data["part_d"]["base_beneficiary_premium_percent"] = {
        "values": {"2006-01-01": 0.255, "2030-01-01": 0.2}
    }
    medicare = ParameterNode("gov.hhs.medicare", data=data)
    root = SimpleNamespace(
        gov=SimpleNamespace(
            hhs=SimpleNamespace(medicare=medicare), bls=PARAMETERS.gov.bls
        ),
        calibration=PARAMETERS.calibration,
    )
    return root, medicare


def test_published_values_take_precedence_and_later_years_follow_the_statute():
    root, medicare = _medicare_tree_with_2027_values()
    extend_medicare_irmaa_thresholds(root, end_year=2030)
    extend_medicare_part_d_irmaa_amounts(root, end_year=2030)
    for program in ("part_b", "part_d"):
        for status in ALL_STATUSES:
            built = _brackets(getattr(medicare, program), status)
            system_brackets = _brackets(getattr(MEDICARE, program), status)
            for index, (bracket, system_bracket) in enumerate(
                zip(built, system_brackets)
            ):
                assert _at(bracket.threshold, 2027) == (
                    _at(bracket.threshold, LAST_ANNOUNCED_YEAR) + 1
                )
                if program == "part_d" and index > 0:
                    assert _at(bracket.amount, 2027) == (
                        _at(bracket.amount, LAST_ANNOUNCED_YEAR) + 1
                    )
                # 2028 on is computed from the statute, as in the system.
                for year in (2028, 2030):
                    assert _at(bracket.threshold, year) == _at(
                        system_bracket.threshold, year
                    )
                    if program == "part_d":
                        assert _at(bracket.amount, year) == _at(
                            system_bracket.amount, year
                        )


# 9. Extension of the new series.

NEW_SERIES = (PART_A_SERIES, DEDUCTIBLE_SERIES, PART_D_SERIES)


@given(st.sampled_from(NEW_SERIES), st.integers(LAST_TRUSTEES_YEAR + 1, END_YEAR))
def test_new_series_extend_at_the_last_trustees_growth_rate(path, year):
    last_growth = _series(path, LAST_TRUSTEES_YEAR) / _series(
        path, LAST_TRUSTEES_YEAR - 1
    )
    growth = _series(path, year) / _series(path, year - 1)
    assert growth == pytest.approx(last_growth, rel=1e-12)


@given(st.sampled_from(NEW_SERIES), st.integers(END_YEAR, END_YEAR + 100))
def test_new_series_hold_their_2100_value(path, year):
    assert _series(path, year) == _series(path, END_YEAR)
