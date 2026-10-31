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

from policyengine_us.tools.social_security.history import (
    EarningsHistory,
    EarningsRecord,
    HistoryParameters,
    aime_from_indexed,
    compute_history,
    compute_history_pia,
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


def test_benchmarks_before1983_and_uninsured_history_rejected():
    with pytest.raises(ValueError, match="before 1983"):
        compute_history(fixture(), 1982, 2039, parameters())
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
