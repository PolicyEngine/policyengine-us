"""Annual reform composition, synthetic ledger, and exact payment pipeline.

These pure service tests retain annual and rational intermediates that the
model's scalar YAML outputs cannot expose. The synthetic fixture is arithmetic,
not a forecast: unit NAWI ratios, zero COLAs, and fixed supplied caps/bends.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction
from itertools import product

from hypothesis import given, settings, strategies as st
import pytest

from policyengine_us.tools.social_security.donut import DonutParameters
from policyengine_us.tools.social_security.history import (
    EarningsHistory,
    EarningsRecord,
    HistoryParameters,
    compute_history,
    compute_history_pia,
)
from policyengine_us.tools.social_security.household import (
    SuppliedRecord,
    calculate_year,
    claiming_factor,
)
from policyengine_us.tools.social_security.mini_pia import compute_mini_pia
from policyengine_us.tools.social_security.owners_draw import (
    OwnersDrawInputs,
    OwnersDrawParameters,
)
from policyengine_us.tools.social_security.pia import compute_pia


D = Decimal
BENDS = (1000, 6000)
DRAW = OwnersDrawParameters(
    in_effect=True,
    start_year=2027,
    phase_in_share=1,
    current_law_cap=120000,
    benefit_credit=True,
)
DONUT = DonutParameters(
    in_effect=True,
    start_year=2027,
    threshold=400000,
    tax_rate=".124",
    credit_enabled=True,
    credit_rate=".02",
)


def _fixture(*, e1=False, mini=False, donut=False):
    records = []
    for year in range(1999, 2039):
        wages = 60000 if 2004 <= year <= 2036 else 500800 if year == 2038 else 0
        owners = OwnersDrawInputs(s_corp_income=60000 if year == 2037 else 0)
        records.append(EarningsRecord(year, wages, 0, owners_draw=owners))
    history = EarningsHistory(
        first_year=1999,
        records=tuple(records),
        certified_zero_before_first_year=True,
    )
    parameters = HistoryParameters(
        wage_base={year: 120000 for year in range(1999, 2039)},
        nawi={year: 1 for year in range(1999, 2039)},
        owners_draw_by_year={year: DRAW for year in range(1999, 2039)} if e1 else None,
        mini_share=Fraction(int(mini)),
        donut_by_year={year: DONUT for year in range(1999, 2039)} if donut else None,
    )
    return history, parameters


EXPECTED_PIA = {
    (False, False, False): "2180.0",
    (True, False, False): "2221.9",
    (False, True, False): "2028.1",
    (False, False, True): "2184.8",
    (True, True, False): "2083.7",
    (True, False, True): "2226.7",
    (False, True, True): "2032.9",
    (True, True, True): "2088.5",
}


@pytest.mark.parametrize("e1,mini,donut", list(product((False, True), repeat=3)))
def test_every_hand_fixture_row_and_all_eight_reform_combinations(e1, mini, donut):
    history, parameters = _fixture(e1=e1, mini=mini, donut=donut)
    calculation = compute_history(history, 2036, 2039, parameters, birth_year=1974)
    assert calculation.aime == (5131 if e1 else 5000)
    assert calculation.aime_plus == (240 if donut else 0)
    assert calculation.donut_credit_pia == (Fraction("4.8") if donut else 0)
    assert calculation.mini_share == int(mini)
    assert compute_history_pia(calculation, bend_points=BENDS) == D(
        EXPECTED_PIA[e1, mini, donut]
    )
    assert len(calculation.ledger) == 40
    for row in calculation.ledger:
        owners_year = e1 and row.year == 2037
        donut_year = donut and row.year == 2038
        ordinary = (
            60000
            if 2004 <= row.year <= 2036
            else 55410
            if owners_year
            else 120000
            if row.year == 2038
            else 0
        )
        assert row.ordinary_cap == 120000
        assert row.ordinary_covered == ordinary
        assert row.indexed_ordinary == ordinary
        assert row.indexing_factor == 1
        assert row.e1_gross == (60000 if owners_year else 0)
        assert row.e1_net_earnings == (55410 if owners_year else 0)
        assert row.e1_credited == (55410 if owners_year else 0)
        assert row.e1_oasdi_base == (55410 if owners_year else 0)
        assert row.e1_niit_exclusion == (60000 if owners_year else 0)
        assert row.donut_taxed == (100800 if donut_year else 0)
        assert row.donut_credited == (100800 if donut_year else 0)
        assert row.indexed_donut == (100800 if donut_year else 0)
    minis = compute_mini_pia(
        [row.indexed_ordinary for row in calculation.ledger], 2036, bend_points=BENDS
    )
    for row, mini_pia in zip(calculation.ledger, minis.annual_mini_pias, strict=True):
        expected_mini = (
            2180
            if 2004 <= row.year <= 2036
            else Fraction("2057.6")
            if e1 and row.year == 2037
            else 3100
            if row.year == 2038
            else 0
        )
        assert mini_pia == expected_mini
    assert minis.mini_pia == (Fraction("77097.6") if e1 else Fraction(75040)) / 37


def test_joint_fixture_reuses_claiming_payment_rounding_and_first_year_timing():
    history, parameters = _fixture(e1=True, mini=True, donut=True)
    record = SuppliedRecord(
        source="history",
        worker_id="synthetic-worker",
        birth_date=date(1974, 1, 2),
        entitlement_month="2039-01",
        insured=True,
        eligibility_year=2036,
        history=history,
        history_parameters=parameters,
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
    )
    assert claiming_factor(record.birth_date, record.entitlement_month) == Fraction(
        13, 15
    )
    before = calculate_year(record, 2038, bend_points=BENDS)
    assert before.entitlement_total == before.payment_total == 0
    claimed = calculate_year(record, 2039, bend_points=BENDS)
    january = next(row for row in claimed.ledger if row.entitlement_month == "2039-01")
    assert january.eligibility_pia == D("2088.5")
    assert abs(january.unrounded_benefit - D("1810.033333333333333333333333")) < D(
        "1e-20"
    )
    assert january.gross_benefit == january.payable_benefit == 1810
    assert claimed.entitlement_total == 21720
    assert claimed.payment_total == 1810 * 11
    full_payment_year = calculate_year(record, 2040, bend_points=BENDS)
    assert (
        full_payment_year.entitlement_total == full_payment_year.payment_total == 21720
    )


def _single(
    *, year=2038, wages=0, se=0, owners=None, draw=DRAW, donut=None, cap=120000
):
    history = EarningsHistory(
        first_year=year,
        records=(
            EarningsRecord(year, wages, se, owners_draw=owners or OwnersDrawInputs()),
        ),
        certified_zero_before_first_year=True,
    )
    parameters = HistoryParameters(
        wage_base={year: cap},
        nawi={year - 2: 1, year: 1},
        owners_draw_by_year={year: draw} if draw else None,
        donut_by_year={year: donut} if donut else None,
    )
    return compute_history(history, year, year + 1, parameters)


def test_e1_credit_enters_before_ordinary_cap():
    calculation = _single(wages=119000, owners=OwnersDrawInputs(s_corp_income=60000))
    row = calculation.ledger[0]
    assert row.e1_net_earnings == row.e1_credited == 55410
    assert row.e1_oasdi_base == 1000
    assert row.ordinary_covered == 120000
    assert calculation.aime == 285


@pytest.mark.parametrize(
    "owners,expected",
    [
        (OwnersDrawInputs(s_corp_income=-10000, partnership_income=20000), "9235"),
        (OwnersDrawInputs(s_corp_income=-10000), "0"),
        (OwnersDrawInputs(s_corp_income=400), "0"),
        (OwnersDrawInputs(s_corp_income=500), "461.75"),
        (
            OwnersDrawInputs(
                s_corp_income=100000,
                passive_income=40000,
                already_se_income=20000,
                passive_se_overlap=10000,
            ),
            "46175",
        ),
        (
            OwnersDrawInputs(
                s_corp_income=100000,
                passive_income=40000,
                already_se_income=20000,
                subsets_are_disjoint=True,
            ),
            "36940",
        ),
    ],
)
def test_e1_losses_floor_and_explicit_subset_overlap(owners, expected):
    row = _single(owners=owners).ledger[0]
    assert row.e1_credited == D(expected)
    assert row.ordinary_covered == D(expected)


def test_e1_ambiguous_subsets_are_rejected_by_shared_kernel():
    with pytest.raises(ValueError, match="overlap"):
        _single(
            owners=OwnersDrawInputs(
                s_corp_income=100000, passive_income=40000, already_se_income=20000
            )
        )


@pytest.mark.parametrize("year,expected", [(2026, 0), (2027, 5541), (2036, 55410)])
def test_e1_linear_phase_is_applied_per_earnings_year(year, expected):
    row = _single(
        year=year,
        owners=OwnersDrawInputs(s_corp_income=60000),
        draw=replace(DRAW, phase_in_share=-1, phase_in_years=10),
    ).ledger[0]
    assert row.e1_credited == expected


def test_e1_netting_factor_tracks_tax_rate_parameters():
    row = _single(
        owners=OwnersDrawInputs(s_corp_income=60000),
        draw=replace(DRAW, oasdi_rate=0.15),
    ).ledger[0]
    assert row.e1_net_earnings == row.e1_credited == 54630


@pytest.mark.parametrize(
    "basis,expected_base,expected_exclusion", [(0, 0, 0), (1, 55410, 60000)]
)
def test_e1_room_cap_basis_is_independent_of_reformed_ordinary_cap(
    basis, expected_base, expected_exclusion
):
    row = _single(
        wages=150000,
        owners=OwnersDrawInputs(s_corp_income=60000),
        cap=1000000,
        draw=replace(DRAW, room_cap_basis=basis),
    ).ledger[0]
    assert row.e1_oasdi_base == expected_base
    assert row.e1_niit_exclusion == expected_exclusion
    assert row.e1_credited == 55410
    assert row.ordinary_covered == 205410


def test_e1_hi_mode_changes_gross_exclusion_above_room():
    row = _single(
        wages=150000,
        owners=OwnersDrawInputs(s_corp_income=60000),
        draw=replace(DRAW, include_hi=True),
    ).ledger[0]
    assert row.e1_oasdi_base == 0
    assert row.e1_niit_exclusion == 60000
    assert row.e1_credited == 55410


def test_e1_credit_switch_does_not_convert_tax_dollars_into_earnings():
    row = _single(
        owners=OwnersDrawInputs(s_corp_income=60000),
        draw=replace(DRAW, benefit_credit=False),
    ).ledger[0]
    assert row.e1_net_earnings == row.e1_oasdi_base == 55410
    assert row.e1_credited == row.ordinary_covered == 0


def test_donut_taxed_draw_is_included_once_even_after_e1_ordinary_room_exhausted():
    row = _single(
        wages=390000,
        owners=OwnersDrawInputs(s_corp_income=60000),
        donut=DONUT,
    ).ledger[0]
    assert row.e1_oasdi_base == 0
    assert row.e1_credited == 55410
    assert row.ordinary_covered == 120000
    assert row.donut_taxed == row.donut_credited == 45410


def test_donut_draw_exclusion_applies_to_tax_and_credit_together():
    row = _single(
        wages=390000,
        owners=OwnersDrawInputs(s_corp_income=60000),
        donut=replace(DONUT, include_owners_draw=False),
    ).ledger[0]
    assert row.e1_credited == 55410
    assert row.donut_taxed == row.donut_credited == 0


def test_donut_pia_factor_uses_the_supplied_eligibility_cohort_coefficient():
    history, parameters = _fixture(donut=True)
    parameters = replace(parameters, donut_credit_rate=Fraction(".03"))
    calculation = compute_history(history, 2036, 2039, parameters)
    assert calculation.aime_plus == 240
    assert calculation.donut_credit_pia == Fraction("7.2")
    assert compute_history_pia(calculation, bend_points=BENDS) == D("2187.2")


def test_mixed_annual_donut_rates_require_an_explicit_cohort_coefficient():
    history = EarningsHistory(
        first_year=2037,
        records=(EarningsRecord(2037, 500800, 0), EarningsRecord(2038, 500800, 0)),
        certified_zero_before_first_year=True,
    )
    parameters = HistoryParameters(
        wage_base={2037: 120000, 2038: 120000},
        nawi={2034: 1, 2037: 1, 2038: 1},
        donut_by_year={2037: DONUT, 2038: replace(DONUT, credit_rate=".03")},
    )
    with pytest.raises(ValueError, match="rate|coefficient"):
        compute_history(history, 2036, 2039, parameters)
    calculation = compute_history(
        history, 2036, 2039, replace(parameters, donut_credit_rate=Fraction(".05"))
    )
    assert calculation.aime_plus == 480
    assert calculation.donut_credit_pia == 24


@settings(max_examples=30, deadline=None)
@given(
    wages=st.lists(
        st.integers(min_value=0, max_value=1000000), min_size=40, max_size=40
    )
)
def test_all_reforms_off_equals_independent_conventional_computation(wages):
    history = EarningsHistory(
        first_year=1999,
        records=tuple(
            EarningsRecord(year, amount, 0)
            for year, amount in zip(range(1999, 2039), wages, strict=True)
        ),
        certified_zero_before_first_year=True,
    )
    parameters = HistoryParameters(
        wage_base={year: 120000 for year in range(1999, 2039)},
        nawi={year: 1 for year in range(1999, 2039)},
    )
    calculation = compute_history(history, 2036, 2039, parameters)
    expected_aime = (
        sum(sorted((min(amount, 120000) for amount in wages), reverse=True)[:35]) // 420
    )
    assert calculation.aime == expected_aime
    assert calculation.aime_plus == calculation.donut_credit_pia == 0
    assert compute_history_pia(calculation, bend_points=BENDS) == compute_pia(
        expected_aime, 2036, bend_points=BENDS
    )


@settings(max_examples=40, deadline=None)
@given(wages=st.integers(min_value=0, max_value=600000))
def test_donut_never_changes_conventional_aime_and_never_credits_gap(wages):
    off = _single(wages=wages, draw=None)
    on = _single(wages=wages, draw=None, donut=DONUT)
    assert on.aime == off.aime
    row = on.ledger[0]
    assert row.donut_credited == max(0, wages - 400000)
    if 120000 < wages <= 400000:
        assert row.donut_taxed == row.donut_credited == 0


@settings(max_examples=40, deadline=None)
@given(
    wages=st.integers(min_value=0, max_value=500000),
    se=st.integers(min_value=0, max_value=50000),
    gross=st.integers(min_value=0, max_value=200000),
)
def test_e1_credit_is_bounded_by_net_draw_and_each_ledger_stream_counts_it_once(
    wages, se, gross
):
    row = _single(
        wages=wages,
        se=se,
        owners=OwnersDrawInputs(s_corp_income=gross),
        donut=DONUT,
    ).ledger[0]
    assert 0 <= row.e1_credited <= row.e1_net_earnings
    assert row.e1_credited == row.e1_net_earnings
    assert row.ordinary_covered == min(D(wages + se) + row.e1_credited, 120000)
    assert (
        row.donut_taxed
        == row.donut_credited
        == max(0, D(wages + se) + row.e1_net_earnings - 400000)
    )


@settings(max_examples=20, deadline=None)
@given(
    payment_year=st.integers(min_value=2030, max_value=2038),
    wages=st.integers(min_value=0, max_value=1000000),
)
def test_benefit_is_zero_before_entitlement_for_any_earnings(payment_year, wages):
    history, parameters = _fixture(e1=True, mini=True, donut=True)
    history = replace(
        history,
        records=history.records[:-1]
        + (replace(history.records[-1], covered_wages=wages),),
    )
    record = SuppliedRecord(
        source="history",
        worker_id="synthetic-worker",
        birth_date=date(1974, 1, 2),
        entitlement_month="2039-01",
        insured=True,
        eligibility_year=2036,
        history=history,
        history_parameters=parameters,
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
    )
    result = calculate_year(record, payment_year, bend_points=BENDS)
    assert result.entitlement_total == result.payment_total == 0
    assert all(row.payable_benefit == 0 for row in result.ledger)
