"""Pure career arithmetic, certification and compatibility with the legacy AIME.

These tests exercise supplied records and pure services without constructing a
country model. API/export behavior has a separate small integration witness.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from types import SimpleNamespace as Node

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from policyengine_core.periods import period
from pathlib import Path

from policyengine_core.parameters import load_parameter_file

from policyengine_us.tools.social_security.donut import DonutParameters
from policyengine_us.tools.social_security.history import (
    EarningsHistory,
    EarningsRecord,
    HistoryParameters,
    aime_from_indexed,
    compute_history,
    compute_history_pia,
    computation_years,
    history_pia_details,
)
from policyengine_us.tools.social_security.household import (
    SuppliedRecord,
    calculate_year,
)
from policyengine_us.tools.social_security.pia import FormulaPath
from policyengine_us.variables.gov.ssa.social_security.ss_aime import _compute_aime


def history(records, first=1999, zeros=()):
    return EarningsHistory(first, tuple(records), tuple(zeros), True)


def parameters(first=1999, last=2038, **overrides):
    return HistoryParameters(
        wage_base={year: 120_000 for year in range(first, last + 1)},
        nawi={year: 100 for year in range(first, last + 1)},
        **overrides,
    )


def fixture():
    return history(
        [EarningsRecord(year, 60_000, 0) for year in range(2004, 2037)]
        + [EarningsRecord(2037, 0, 0), EarningsRecord(2038, 500_800, 0)],
        zeros=range(1999, 2004),
    )


def worker(source="history", **kwargs):
    return SuppliedRecord(
        source=source,
        worker_id="worker",
        birth_date=date(1974, 1, 2),
        entitlement_month="2039-01",
        insured=True,
        eligibility_year=2036,
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
        **kwargs,
    )


def test_hand_computed_conventional_rows_and_payment_pipeline():
    career = compute_history(fixture(), 2036, 2039, parameters(), birth_year=1974)
    assert career.aime == 5000
    assert [row.ordinary_covered for row in career.ledger[:5]] == [0] * 5
    assert [row.indexed_ordinary for row in career.ledger[5:38]] == [60_000] * 33
    assert career.ledger[-2].ordinary_covered == 0
    assert career.ledger[-1].ordinary_covered == 120_000
    assert compute_history_pia(career, bend_points=(1000, 6000)) == Decimal("2180")
    annual = calculate_year(
        worker(history=fixture(), history_parameters=parameters()),
        2039,
        bend_points=(1000, 6000),
    )
    january = annual.ledger[1]
    assert january.claiming_factor == Decimal(13) / 15
    assert january.payable_benefit == 1889
    assert annual.entitlement_total == 1889 * 12
    # A January entitlement is first paid in February (merged 4a-1 contract).
    assert annual.payment_total == 1889 * 11


def test_cap_before_indexing_half_up_cents_and_face_value_from_e_minus_two():
    supplied = history(
        [EarningsRecord(y, 150_000, 0) for y in range(2033, 2039)], first=2033
    )
    p = parameters()
    p = replace(p, nawi={2033: 96, 2034: 100, 2035: 80, 2036: 75, 2037: 70, 2038: 60})
    result = compute_history(supplied, 2036, 2039, p)
    assert result.ledger[0].indexed_ordinary == 125_000
    assert [row.indexed_ordinary for row in result.ledger[1:]] == [120_000] * 5
    cents = compute_history(
        history([EarningsRecord(2033, ".005", 0)], first=2033, zeros=range(2034, 2039)),
        2036,
        2039,
        replace(p, nawi={2033: 100, 2034: 100}),
    )
    assert cents.ledger[0].indexed_ordinary == Decimal(".01")


def test_top35_padding_and_whole_dollar_truncation():
    assert aime_from_indexed([Decimal(420)] * 40) == 35
    assert aime_from_indexed([Decimal("419.99")]) == 0
    assert aime_from_indexed([Decimal(420)]) == 1
    assert aime_from_indexed([]) == 0


# --- Cohort computation years (42 U.S.C. 415(b)(2)) -------------------------
# Elapsed years run from 1951 through the year before age-62 eligibility E,
# and the computation period is elapsed years less five (POMS RS 00605.016
# and RS 00605.017): min(35, E - 1956) for the supported benchmarks from 1984.
# 42 U.S.C. 415(a)(4)(B)(i) keeps the December 1978 computation, when larger,
# for workers eligible before 1984, so the history route refuses E <= 1983.

SSA_PARAMETERS = Path(__file__).parents[2] / "parameters" / "gov" / "ssa"


@pytest.fixture(scope="module")
def ssa_parameters():
    """Load only the branch's historical caps, NAWI and bend points.

    Reading the four YAML files avoids building the country model; the
    historical values used here need no uprating.
    """
    files = {
        "wage_base": "social_security/wage_base.yaml",
        "nawi": "nawi.yaml",
        "first": "social_security/pia/bend_points/first.yaml",
        "second": "social_security/pia/bend_points/second.yaml",
    }
    return {
        name: load_parameter_file(str(SSA_PARAMETERS / path), name)
        for name, path in files.items()
    }


def _real_parameters(ssa_parameters, eligibility, years):
    def value(name, year):
        return Decimal(str(ssa_parameters[name](f"{year}-01-01")))

    return HistoryParameters(
        wage_base={year: value("wage_base", year) for year in years},
        nawi={year: value("nawi", year) for year in set(years) | {eligibility - 2}},
    )


def _real_bends(ssa_parameters, eligibility):
    return tuple(
        ssa_parameters[name](f"{eligibility}-01-01") for name in ("first", "second")
    )


def _flat_career(wages, first=1951, last=None, zeros=()):
    years = range(first, last + 1)
    return EarningsHistory(
        1951,
        tuple(EarningsRecord(year, wages, 0) for year in years if year not in zeros),
        tuple(zeros),
    )


def test_computation_years_follow_the_elapsed_years_rule():
    assert computation_years(1984) == 28
    assert computation_years(1990) == 34
    assert computation_years(1991) == 35
    assert computation_years(2036) == 35
    for year in (1983, 1982):
        with pytest.raises(ValueError, match=r"before 1984.*415\(a\)\(4\)\(B\)\(i\)"):
            computation_years(year)


def test_1990_witness_selects_34_years_and_divides_by_408(ssa_parameters):
    """Birth 1928-01-02; $3,000 a year 1951-1989; eligibility and claim 1990.

    NAWI(1988) = 19,334.04 indexes 1951-1987; 1988-1989 stay at face value.
    The highest 34 indexed years sum to $372,486.21 (the highest 35 would sum
    to $375,934.10). AIME = floor(372,486.21 / 408) = $912, not
    floor(375,934.10 / 420) = $895. With 1990 bends $356 / $2,145:
    .9 x 356 + .32 x (912 - 356) = 498.32, floored to $498.30. FRA is 65, so
    a January 1990 claim at 62 has factor 0.8: 398.64, paid as $398.
    """
    years = range(1951, 1990)
    career = _flat_career(3000, last=1989)
    parameters = _real_parameters(ssa_parameters, 1990, years)
    result = compute_history(career, 1990, 1990, parameters, birth_year=1928)
    top = sorted((row.indexed_ordinary for row in result.ledger), reverse=True)
    assert result.computation_years == 34
    assert sum(top[:34]) == Decimal("372486.21")
    assert sum(top[:35]) == Decimal("375934.10")
    assert result.aime == 912
    bends = _real_bends(ssa_parameters, 1990)
    assert bends == (356, 2145)
    assert compute_history_pia(result, bend_points=bends) == Decimal("498.3")
    annual = calculate_year(
        SuppliedRecord(
            source="history",
            worker_id="witness-1990",
            birth_date=date(1928, 1, 2),
            entitlement_month="1990-01",
            insured=True,
            eligibility_year=1990,
            history=career,
            history_parameters=parameters,
            no_special_monthly_test=True,
            no_prior_withholding_adjustment=True,
            earnings_test_no_trigger=True,
        ),
        1990,
        bend_points=bends,
    )
    january = next(row for row in annual.ledger if row.entitlement_month == "1990-01")
    assert january.claiming_factor == Decimal("0.8")
    assert january.eligibility_pia == Decimal("498.3")
    assert january.payable_benefit == 398


@pytest.mark.parametrize(
    "eligibility,years,top_sum,aime,pia",
    [
        # 1984: NAWI(1982) 14,531.34 indexes 1951-1981; the highest 28 are
        # 1951-1978 (1979-1983 drop). Sum/336 = 776.63; bends 267 / 1,612:
        # 240.30 + .32 x 509 = 403.18 -> $403.10.
        (1984, 28, "260949.26", 776, "403.1"),
        # 1990: the witness above.
        (1990, 34, "372486.21", 912, "498.3"),
        # 1991: NAWI(1989) 20,099.55; sum/420 = 930.52; bends 370 / 2,230:
        # 333.00 + .32 x 560 = 512.20.
        (1991, 35, "390818.79", 930, "512.2"),
    ],
)
def test_cohort_boundaries_select_28_34_and_35_years(
    ssa_parameters, eligibility, years, top_sum, aime, pia
):
    career = _flat_career(3000, last=eligibility - 1)
    parameters = _real_parameters(ssa_parameters, eligibility, range(1951, eligibility))
    result = compute_history(
        career, eligibility, eligibility, parameters, birth_year=eligibility - 62
    )
    top = sorted((row.indexed_ordinary for row in result.ledger), reverse=True)
    assert result.computation_years == years
    assert sum(top[:years]) == Decimal(top_sum)
    assert result.aime == aime == int(Decimal(top_sum) // (12 * years))
    bends = _real_bends(ssa_parameters, eligibility)
    assert compute_history_pia(result, bend_points=bends) == Decimal(pia)


def test_35_year_cohort_still_divides_by_420(ssa_parameters):
    # Forty $3,000 years for E=2000: only the divisor 420 reproduces AIME.
    eligibility = 2000
    career = _flat_career(3000, first=1960, last=1999)
    career = replace(career, first_year=1960, certified_zero_before_first_year=True)
    parameters = _real_parameters(ssa_parameters, eligibility, range(1960, 2000))
    result = compute_history(career, eligibility, eligibility, parameters)
    top = sorted((row.indexed_ordinary for row in result.ledger), reverse=True)
    assert result.computation_years == 35
    assert result.aime == int(sum(top[:35]) // 420)
    assert result.aime != int(sum(top[:34]) // 408)


def test_zero_extra_year_moves_aime_through_the_divisor_alone(ssa_parameters):
    """E=1990 with $3,000 only in 1956-1989 (34 years); 1951-1955 are zero.

    The 34 nonzero years are the same whichever count is selected, so the
    35th selected year is a certified zero and only the divisor differs.
    """
    years = range(1951, 1990)
    zeros = tuple(range(1951, 1956))
    career = _flat_career(3000, last=1989, zeros=zeros)
    parameters = _real_parameters(ssa_parameters, 1990, years)
    result = compute_history(career, 1990, 1990, parameters, birth_year=1928)
    nonzero = sum(row.indexed_ordinary for row in result.ledger)
    assert sum(row.indexed_ordinary for row in result.ledger[:5]) == 0
    assert result.aime == int(nonzero // 408)
    assert int(nonzero // 420) < result.aime


def test_aime_plus_keeps_35_years_for_a_short_cohort():
    # Flat NAWI and a $120,000 cap. One 1989 year of $404,080 credits $4,080
    # above a $400,000 donut threshold: AIME+ floor(4,080 / 420) = 9, while a
    # 34-year count would give floor(4,080 / 408) = 10.
    donut = DonutParameters(
        in_effect=True,
        start_year=1951,
        threshold=400000,
        tax_rate=".124",
        credit_enabled=True,
        credit_rate=".02",
    )
    years = range(1951, 1990)
    career = EarningsHistory(
        1951,
        tuple(
            EarningsRecord(year, 404_080 if year == 1989 else 0, 0) for year in years
        ),
    )
    result = compute_history(
        career,
        1990,
        1990,
        HistoryParameters(
            wage_base={year: 120_000 for year in years},
            nawi={year: 1 for year in years},
            donut_by_year={year: donut for year in years},
        ),
    )
    assert result.computation_years == 34
    assert result.aime == 120_000 // 408
    assert result.aime_plus == 9


def test_after62_through_previous_claim_year_and_no_post_claim_recomputation():
    records = [EarningsRecord(y, 0, 0) for y in range(2036, 2041)]
    records[2] = EarningsRecord(2038, 100_800, 0)
    records[3] = EarningsRecord(2039, 120_000, 0)
    supplied = history(records, first=2036)
    result = compute_history(supplied, 2036, 2039, parameters())
    assert result.aime == 240
    record = worker(history=supplied, history_parameters=parameters())
    assert calculate_year(record, 2040, bend_points=(1000, 6000)).history == result


@pytest.mark.parametrize(
    "reform",
    [
        FormulaPath(),
        FormulaPath(factor_values=(".95", ".32", ".05")),
        FormulaPath(bend_point_multipliers=("1.18", 1)),
    ],
)
def test_4d_identical_supplied_aime_and_history_pia(reform):
    record = worker(history=fixture(), history_parameters=parameters())
    supplied = worker("aime", aime=5000)
    actual = calculate_year(record, 2040, bend_points=(1000, 6000), formula_path=reform)
    expected = calculate_year(
        supplied, 2040, bend_points=(1000, 6000), formula_path=reform
    )
    assert actual.ledger == expected.ledger
    assert actual.entitlement_total == expected.entitlement_total


def test_missing_versus_zero_certification_and_json():
    supplied = EarningsHistory.from_json(
        '{"first_year":2037,"certified_zero_before_first_year":true,"records":[{"year":2038,"covered_wages":"420.00","covered_self_employment":"0"}]}'
    )
    with pytest.raises(ValueError, match="Missing required.*2037"):
        compute_history(supplied, 2036, 2039, parameters())
    assert (
        compute_history(
            replace(supplied, certified_zero_years=(2037,)), 2036, 2039, parameters()
        ).aime
        == 1
    )
    with pytest.raises(ValueError, match="Certify zero"):
        compute_history(
            replace(supplied, certified_zero_before_first_year=False),
            2036,
            2039,
            parameters(),
        )
    with pytest.raises(ValueError, match="conflicting"):
        compute_history(
            replace(supplied, certified_zero_years=(2037, 2038)),
            2036,
            2039,
            parameters(),
        )


@pytest.mark.parametrize("bad", [None, True, "NaN", "Infinity", -1])
def test_invalid_covered_earnings_rejected(bad):
    with pytest.raises(ValueError, match="finite nonnegative"):
        compute_history(
            history([EarningsRecord(2038, bad, 0)], first=2038),
            2036,
            2039,
            parameters(),
        )


def test_duplicate_year_unknown_field_and_missing_se_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        compute_history(
            history([EarningsRecord(2038, 0, 0)] * 2, first=2038),
            2036,
            2039,
            parameters(),
        )
    for payload in (
        '{"first_year":2038,"unknown":0}',
        '{"first_year":2038,"records":[{"year":2038,"covered_wages":0}]}',
    ):
        with pytest.raises(ValueError, match="Invalid annual"):
            EarningsHistory.from_json(payload)


EARLY = r"before 1984.*415\(a\)\(4\)\(B\)\(i\)"


@pytest.mark.parametrize("eligibility", [1983, 1982])
def test_benchmarks_before1984_rejected_at_each_history_entry_point(eligibility):
    birth = date(eligibility - 62, 1, 2)
    with pytest.raises(ValueError, match=EARLY):
        computation_years(eligibility)
    with pytest.raises(ValueError, match=EARLY):
        compute_history(fixture(), eligibility, 2039, parameters())
    record = replace(
        worker(history=fixture(), history_parameters=parameters()),
        birth_date=birth,
        entitlement_month=f"{eligibility}-02",
        eligibility_year=eligibility,
    )
    with pytest.raises(ValueError, match=EARLY):
        record.benchmark()
    if eligibility == 1983:
        # Supplied AIME and PIA sources keep their own 1983 start.
        assert replace(record, source="aime", aime=1000).benchmark() == 1983
        assert replace(record, source="pia", pia=500).benchmark() == 1983
    early = replace(
        compute_history(fixture(), 2036, 2039, parameters()),
        eligibility_year=eligibility,
    )
    with pytest.raises(ValueError, match=EARLY):
        history_pia_details(early, bend_points=(254, 1528))


def test_history_benchmark_boundary_follows_age_62_attainment():
    # GN 00302.400: a January 1, 1922 birth attains 62 on December 31, 1983.
    record = replace(
        worker(history=fixture(), history_parameters=parameters()),
        entitlement_month="1984-02",
    )
    with pytest.raises(ValueError, match=EARLY):
        replace(record, birth_date=date(1922, 1, 1), eligibility_year=1983).benchmark()
    assert (
        replace(record, birth_date=date(1922, 1, 2), eligibility_year=1984).benchmark()
        == 1984
    )


def test_annual_records_cannot_begin_before_1951():
    early = EarningsHistory(1950, (EarningsRecord(1950, 3000, 0),))
    with pytest.raises(ValueError, match="base years"):
        early.through_claim(1984)


def test_uninsured_history_rejected():
    with pytest.raises(ValueError, match="insured-status"):
        replace(worker(), insured=False).benchmark()


def test_benefit_zero_before_entitlement():
    result = calculate_year(
        worker(history=fixture(), history_parameters=parameters()),
        2038,
        bend_points=(1000, 6000),
    )
    assert result.entitlement_total == result.payment_total == 0


@settings(max_examples=50, deadline=None)
@given(
    st.lists(st.integers(min_value=0, max_value=1_000_000), min_size=1, max_size=45),
    st.integers(min_value=0, max_value=1_000_000),
)
def test_aime_nondecreasing_in_any_earnings_year(earnings, extra):
    # Cycle the changed position to cover both selected and unselected years.
    position = extra % len(earnings)
    bumped = list(earnings)
    bumped[position] += extra
    assert aime_from_indexed(bumped) >= aime_from_indexed(earnings)


@settings(max_examples=50, deadline=None)
@given(
    annual=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=1_000_000),
            st.integers(min_value=0, max_value=50_000),
            st.integers(min_value=60_000, max_value=200_000),
            st.integers(min_value=50, max_value=500),
        ),
        min_size=1,
        max_size=45,
    ),
    position=st.integers(min_value=0, max_value=44),
    extra=st.integers(min_value=0, max_value=1_000_000),
)
def test_history_aime_nondecreasing_when_any_years_covered_wages_increase(
    annual, position, extra
):
    """Exercise annual cap, E-2 indexing, cents, top 35, and whole-dollar AIME."""
    first = 2039 - len(annual)
    years = tuple(range(first, 2039))
    supplied = history(
        [
            EarningsRecord(year, wages, se)
            for year, (wages, se, _, _) in zip(years, annual, strict=True)
        ],
        first=first,
    )
    nawi = {year: values[3] for year, values in zip(years, annual, strict=True)}
    nawi.setdefault(2034, 100)
    policy = HistoryParameters(
        wage_base={year: values[2] for year, values in zip(years, annual, strict=True)},
        nawi=nawi,
    )
    changed_position = position % len(annual)
    bumped_records = list(supplied.records)
    original = bumped_records[changed_position]
    bumped_records[changed_position] = replace(
        original, covered_wages=original.covered_wages + extra
    )
    original_aime = compute_history(supplied, 2036, 2039, policy).aime
    bumped_aime = compute_history(
        replace(supplied, records=tuple(bumped_records)), 2036, 2039, policy
    ).aime
    assert bumped_aime >= original_aime


def test_legacy_aime_differential_on_shared_year_window_and_exact_rounding():
    """Independent old NumPy formula agrees where its window/rounding match."""
    wages = {year: 50_400 for year in range(1986, 2026)}
    p = Node(
        indexing_age=60,
        minimum_age_for_earnings=22,
        max_earnings_age=62,
        years_of_earnings=35,
        months_per_year=12,
    )

    class Person:
        count = 1

        def __call__(self, name, when):
            return np.array(
                [
                    62
                    if name == "age"
                    else wages.get(when.start.year, 0)
                    if name == "employment_income"
                    else 0
                ]
            )

    def policy(when):
        year = when.start.year
        nawi = 50 if year < 2024 else 100
        return Node(
            gov=Node(
                ssa=Node(nawi=nawi, social_security=Node(aime=p, wage_base=120_000)),
                simulation=Node(aime_lookback_years=40),
            )
        )

    years = range(1986, 2026)
    career = compute_history(
        history([EarningsRecord(y, wages[y], 0) for y in years], first=1986),
        2026,
        2026,
        HistoryParameters(
            {y: 120_000 for y in years}, {y: 50 if y < 2024 else 100 for y in years}
        ),
    )
    legacy = _compute_aime(Person(), period("2026"), policy)
    assert legacy[0] == career.aime == 8400
