"""Acceptance tests for identified supplied-record household calculations.

SSA examples are cited locally. Synthetic cases keep eligibility PIA, COLAs,
claiming, earnings testing and check-month timing independently observable.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction

import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us.tools.social_security.cola import ColaEvent, apply_colas
from policyengine_us.tools.social_security.household import (
    BenefitPolicies,
    SuppliedRecord,
    SurvivorBasis,
    calculate_year,
    claiming_factor,
    full_retirement_age_months,
)
from policyengine_us.tools.social_security.pia import FormulaPath


D = Decimal
BENDS = (960, 5785)


def retirement(**overrides):
    values = dict(
        source="pia",
        worker_id="worker-1",
        birth_date=date(1960, 1, 2),
        eligibility_year=2022,
        entitlement_month="2022-01",
        insured=True,
        pia=D(1000),
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
    )
    values.update(overrides)
    return SuppliedRecord(**values)


def survivor_basis(**overrides):
    values = dict(
        worker_birth_year=1970,
        death_year=2020,
        worker_birth_date=date(1970, 6, 15),
        death_date=date(2020, 8, 12),
        provenance="Supplied worker birth and death dates",
        no_prior_disability=True,
        ordinary_non_windex=True,
    )
    values.update(overrides)
    return SurvivorBasis(**values)


def survivor(**overrides):
    values = dict(
        source="survivor",
        worker_id="deceased-worker-1",
        birth_date=date(1950, 1, 2),
        entitlement_month="2021-01",
        insured=True,
        survivor=survivor_basis(),
        monthly_amount=D(2000),
        valuation_month="2025-01",
        composite_ratio=D(1),
        ratio_description="Supplied composite includes all survivor reductions and delayed credits",
        nonbinding_rib_lim=True,
        nonbinding_family_maximum=True,
        no_dual_entitlement=True,
        no_earnings_test_at_valuation=True,
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
    )
    values.update(overrides)
    return SuppliedRecord(**values)


def compute(record, year=2026, **kwargs):
    return calculate_year(record, year, bend_points=BENDS, **kwargs)


def row_for(result, entitlement_month):
    return next(
        row for row in result.ledger if row.entitlement_month == entitlement_month
    )


def test_ssa_published_supplied_aime_and_pia_claim_at_62():
    # 2023 Supplement Appendix D: E2023 AIME3000 -> PIA1606.70;
    # claiming at62 with FRA67 -> monthly1124 after statutory rounding.
    # https://www.ssa.gov/policy/docs/statcomps/supplement/2023/apnd.html
    record = retirement(
        source="aime",
        aime=3000,
        birth_date=date(1961, 1, 2),
        eligibility_year=2023,
        entitlement_month="2023-01",
    )
    direct = calculate_year(record, 2023, bend_points=(1115, 6721))
    supplied = calculate_year(
        replace(record, source="pia", pia=D("1606.7")), 2023, bend_points=(1115, 6721)
    )
    assert row_for(direct, "2023-01").eligibility_pia == D("1606.7")
    assert direct.entitlement_total == D(1124 * 12)
    assert direct.payment_total == D(1124 * 11)
    assert direct.ledger == supplied.ledger


@pytest.mark.parametrize("source", ["aime", "pia"])
def test_explicit_source_selector_preserves_supplied_zero(source):
    record = retirement(
        source=source,
        aime=0 if source == "aime" else 5000,
        pia=0 if source == "pia" else 1000,
    )
    result = compute(
        record, formula_path=FormulaPath(s770=True), recompute_mode="retroactive"
    )
    assert result.entitlement_total == 0
    assert result.payment_total == 0
    assert all(row.eligibility_pia == 0 for row in result.ledger)
    assert result.inferred_aime_interval is None


@pytest.mark.parametrize(
    "path",
    [
        FormulaPath(effective_year=2032, bend_point_multipliers=(D("1.1"), 1)),
        FormulaPath(
            factor_start_year=2032, factor_values=(D(".9"), D(".32"), D(".05"))
        ),
        FormulaPath(full_price_indexing_start_year=2032),
        FormulaPath(progressive_price_indexing_start_year=2032),
        FormulaPath(s770=True),
        FormulaPath(effective_year=2026),
    ],
)
def test_inactive_or_identity_pia_paths_preserve_supplied_pia_without_inversion(path):
    # A cohort-only reform cannot require inference for this 2022 cohort.
    record = retirement(pia=D("1000.1"))
    baseline = compute(record)
    result = compute(record, formula_path=path)
    assert result.ledger == baseline.ledger
    assert result.inferred_aime_interval is None


@pytest.mark.parametrize("source", ["aime", "pia", "survivor"])
def test_cola_iterators_preserve_the_same_history_for_every_ledger_read(source):
    record = (
        survivor(monthly_amount=D(2200))
        if source == "survivor"
        else retirement(source=source, aime=3000)
    )
    events = [
        ColaEvent("2020-12", "2021-01", D(".1")),
        ColaEvent("2022-12", "2023-01", D(".02")),
    ]
    assert compute(record, cola_events=iter(events)) == compute(
        record, cola_events=events
    )


@pytest.mark.parametrize(
    "age,year,factor,monthly",
    [
        (62, 2022, Fraction(7, 10), 700),
        (65, 2025, Fraction(13, 15), 866),
        (67, 2027, Fraction(1), 1000),
        (70, 2030, Fraction(31, 25), 1240),
    ],
)
def test_exact_claiming_months_62_65_fra_70(age, year, factor, monthly):
    record = retirement(entitlement_month=f"{year}-01")
    assert claiming_factor(record.birth_date, record.entitlement_month) == factor
    assert compute(record, year).entitlement_total == D(monthly * 12)


def test_claiming_uses_months_and_birth_cohort_fra():
    assert full_retirement_age_months(date(1956, 4, 2)) == 796
    assert full_retirement_age_months(date(1960, 1, 2)) == 804
    # One month early is 1 - 5/9 of one percent, not a whole-year age band.
    assert claiming_factor(date(1960, 1, 2), "2026-12") == Fraction(179, 180)


def test_ssa_published_delayed_retirement_credit_example():
    # https://www.ssa.gov/policy/docs/statcomps/supplement/2023/apnd.html
    # DOB April1956, FRA August2022, claim January2023, five DRC months.
    record = retirement(
        birth_date=date(1956, 4, 2),
        eligibility_year=2018,
        entitlement_month="2023-01",
        pia=D("1553.9"),
    )
    result = compute(record, 2023)
    assert row_for(result, "2023-01").payable_benefit == D(1605)


def test_midyear_claim_defers_current_calendar_year_drcs_until_january():
    # https://secure.ssa.gov/poms.nsf/lnx/0300615690
    record = retirement(
        birth_date=date(1956, 4, 2),
        eligibility_year=2018,
        entitlement_month="2023-07",
        pia=D("1500"),
    )
    current, following = compute(record, 2023), compute(record, 2024)
    assert row_for(current, "2023-07").payable_benefit == D(1550)
    assert row_for(following, "2024-01").payable_benefit == D(1610)


def test_partial_year_distinguishes_entitlement_month_and_check_month():
    record = retirement(
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-07",
        supplied_claiming_factor=D(1),
    )
    events = [ColaEvent("2026-12", "2027-01", D(".1"))]
    current = compute(record, 2026, cola_events=events)
    following = compute(record, 2027, cola_events=events)
    assert current.entitlement_total == 6100  # July-Nov1000; Dec1100.
    assert current.payment_total == 5000  # Five checks August-December.
    assert following.payment_total == 13200
    assert row_for(current, "2026-12").payment_month == "2027-01"


def test_colas_from_eligibility_include_years_before_claiming():
    record = retirement(entitlement_month="2027-01", supplied_claiming_factor=D(1))
    events = [
        ColaEvent("2022-12", "2023-01", D(".1")),
        ColaEvent("2023-12", "2024-01", D(".1")),
    ]
    result = compute(record, 2027, cola_events=events)
    assert row_for(result, "2027-01").cola_pia == 1210
    assert result.entitlement_total == 14520


def test_insured_status_is_an_explicit_input():
    result = compute(retirement(insured=False))
    assert result.entitlement_total == result.payment_total == 0


def test_supplied_claiming_factor_is_used_once():
    result = compute(retirement(supplied_claiming_factor=D(".8")))
    assert result.entitlement_total == 9600


def test_known_pia_and_aime_use_the_same_reformed_service():
    known = retirement(pia=D(1000), supplied_claiming_factor=D(".7"))
    direct = replace(known, source="aime", aime=1385)
    options = dict(formula_path=FormulaPath(s770=True), recompute_mode="retroactive")
    assert compute(known, **options).ledger == compute(direct, **options).ledger
    assert row_for(compute(known, **options), "2026-01").eligibility_pia == D("1156.8")


def test_every_month_is_zero_in_year_before_commencement():
    result = compute(retirement(entitlement_month="2030-01"))
    assert result.entitlement_total == result.payment_total == 0
    assert all(row.payable_benefit == 0 for row in result.ledger)


def test_retired_couple_keeps_independent_worker_records():
    first = retirement(
        worker_id="first-worker",
        entitlement_month="2027-01",
        supplied_claiming_factor=D(1),
    )
    second = retirement(
        worker_id="second-worker",
        pia=D(1500),
        entitlement_month="2027-01",
        supplied_claiming_factor=D(".8"),
    )
    assert compute(first, 2027).entitlement_total == 12000
    assert compute(second, 2027).entitlement_total == 14400
    assert (
        compute(first, 2027).entitlement_total + compute(second, 2027).entitlement_total
        == 26400
    )


def test_combined_pia_cola_across_board_and_payable_policies_apply_once():
    record = retirement(
        source="aime",
        aime=5000,
        birth_date=date(1958, 1, 2),
        eligibility_year=2020,
        entitlement_month="2020-01",
        supplied_claiming_factor=D(".7"),
    )
    event = ColaEvent("2020-12", "2021-01", D(".1"))
    policies = BenefitPolicies(
        cola_rates={"2021-01": D(".11")},
        across_the_board={2026: D(".1")},
        payable_share={2026: D(".8")},
    )
    result = compute(
        record,
        formula_path=FormulaPath(s770=True),
        cola_events=[event],
        policies=policies,
        recompute_mode="retroactive",
    )
    row = row_for(result, "2026-01")
    assert row.eligibility_pia == D("2313.6")
    assert row.cola_pia == D("2568.0")
    assert row.payable_benefit == 1581  # 2568 x .7 x 1.1 x .8 ->1581.888.


def test_joint_cola_withholding_bypasses_a_simultaneous_cola_increase():
    record = retirement(entitlement_month="2027-01", supplied_claiming_factor=D(1))
    event = ColaEvent("2026-12", "2027-01", D(".02"))
    result = compute(
        record,
        2027,
        cola_events=[event],
        policies=BenefitPolicies(cola_rates={"2027-01": D(0)}),
    )
    assert result.entitlement_total == 12000


def test_complete_payable_cut_is_valid_and_negative_benefits_are_rejected():
    record = retirement(supplied_claiming_factor=D(1))
    assert (
        compute(
            record, policies=BenefitPolicies(payable_share={2026: D(0)})
        ).payment_total
        == 0
    )
    assert (
        compute(
            record, policies=BenefitPolicies(across_the_board={2026: D(-1)})
        ).payment_total
        == 0
    )
    for policies in (
        BenefitPolicies(payable_share={2026: D("1.01")}),
        BenefitPolicies(payable_share={2026: D("-.01")}),
        BenefitPolicies(across_the_board={2026: D("-1.01")}),
    ):
        with pytest.raises(ValueError):
            compute(record, policies=policies)


def test_ssa_published_under_fra_earnings_test():
    # https://www.ssa.gov/benefits/retirement/planner/whileworking.html
    record = retirement(
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-01",
        pia=D(800),
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    result = compute(record, earnings={2026: 33400}, lower_exempt={2026: 24480})
    assert result.earnings_test_reduction == 4460
    assert result.entitlement_total == 5140
    assert all(
        row.earnings_test_reduction <= row.gross_benefit for row in result.ledger
    )


def test_ssa_published_fra_year_earnings_test_counts_only_pre_fra_months():
    # https://www.ssa.gov/benefits/retirement/planner/whileworking.html
    # Birth October1959 yields retirement FRA66y10m in August2026.
    record = retirement(
        birth_date=date(1959, 10, 2),
        eligibility_year=2021,
        entitlement_month="2026-01",
        pia=D(800),
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    result = compute(
        record,
        earnings={2026: 1_000_000},
        pre_fra_earnings={2026: 66000},
        higher_exempt={2026: 65160},
    )
    assert result.earnings_test_reduction == 280
    assert result.entitlement_total == 9320
    assert (
        sum(
            row.payable_benefit
            for row in result.ledger
            if "2026-08" <= row.entitlement_month <= "2026-12"
        )
        == 4000
    )


def test_earnings_test_floors_work_deduction_before_monthly_allocation():
    # RS02501.080 drops cents from excess earnings /2 or /3.
    # https://secure.ssa.gov/poms.nsf/links/0302501080
    record = retirement(
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-01",
        pia=D(800),
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    result = compute(record, earnings={2026: 24481}, lower_exempt={2026: 24480})
    assert result.earnings_test_reduction == 0
    assert result.entitlement_total == 9600


def test_earnings_after_retirement_fra_do_not_reduce_benefits():
    record = retirement(
        entitlement_month="2027-01",
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    assert compute(record, 2027, earnings={2027: 1_000_000}).entitlement_total == 12000


def test_previous_december_withholding_and_request_order_are_consistent():
    record = retirement(
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-01",
        pia=D(800),
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    inputs = dict(
        earnings={2026: 43080, 2027: 0}, lower_exempt={2026: 24480, 2027: 24480}
    )
    later = compute(record, 2027, **inputs)
    earlier = compute(record, 2026, **inputs)
    assert row_for(earlier, "2026-12") == row_for(later, "2026-12")
    assert later.payment_total == 9100  # December2026 remaining check300 +11x800.


def test_no_earnings_test_assertion_rejects_conflicting_observed_earnings():
    with pytest.raises(ValueError, match="conflicts"):
        compute(retirement(), earnings={2025: 30000}, lower_exempt={2025: 20000})


@pytest.mark.parametrize(
    "assertion", ["no_special_monthly_test", "no_prior_withholding_adjustment"]
)
def test_restricted_worker_route_requires_special_rule_assertions(assertion):
    with pytest.raises(ValueError, match="Assert"):
        compute(retirement(**{assertion: False}))


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "unknown"},
        {"worker_id": ""},
        {"source_basis": "already_reformed"},
        {"source": "aime", "aime": D("1.5")},
        {"source": "aime", "aime": -1},
        {"pia": D("1.05")},
        {"pia": -1},
        {"eligibility_year": 2023},
        {"supplied_claiming_factor": D(0)},
    ],
)
def test_invalid_or_ambiguous_retirement_inputs_fail(changes):
    with pytest.raises(ValueError):
        compute(retirement(**changes))


def test_first_reduced_retirement_month_and_january_1_cohort():
    record = retirement(
        birth_date=date(1964, 6, 3), eligibility_year=2026, entitlement_month="2026-06"
    )
    with pytest.raises(ValueError, match="first eligible month"):
        compute(record)
    assert compute(replace(record, entitlement_month="2026-07")).entitlement_total > 0
    january = retirement(
        birth_date=date(1964, 1, 1), eligibility_year=2025, entitlement_month="2026-01"
    )
    assert january.benchmark() == 2025
    assert full_retirement_age_months(date(1960, 1, 1)) == 802


def test_rejects_retirement_benchmark_before_1983():
    with pytest.raises(ValueError, match="before 1983"):
        compute(
            retirement(
                birth_date=date(1920, 1, 2),
                eligibility_year=1982,
                entitlement_month="1982-01",
            )
        )


def test_survivor_authoritative_and_derived_benchmarks():
    basis = survivor_basis()
    assert basis.benchmark() == (2020, True)
    assert replace(
        basis,
        authoritative_year=2018,
        no_prior_disability=False,
        provenance="Authoritative computation year",
    ).benchmark() == (2018, True)
    after62 = survivor_basis(
        worker_birth_year=1950, worker_birth_date=date(1950, 6, 15), death_year=2020
    )
    assert after62.benchmark() == (2012, False)


def test_survivor_january_1_birth_and_same_year_date_disambiguation():
    basis = survivor_basis(
        worker_birth_year=1964,
        worker_birth_date=date(1964, 1, 1),
        death_year=2026,
        death_date=date(2026, 6, 15),
    )
    assert basis.benchmark() == (2025, False)
    same = survivor_basis(
        worker_birth_year=1964,
        worker_birth_date=date(1964, 6, 15),
        death_year=2026,
        death_date=date(2026, 6, 13),
    )
    assert same.benchmark() == (2026, True)
    assert replace(same, death_date=date(2026, 6, 14)).benchmark() == (2026, False)


def test_survivor_year_only_fallback_requires_stated_assumption_and_same_year_assertion():
    basis = survivor_basis(worker_birth_date=None, death_date=None)
    with pytest.raises(ValueError, match="not-January-1"):
        basis.benchmark()
    assert replace(basis, year_only_not_january_1=True).benchmark() == (2020, True)
    same = replace(basis, worker_birth_year=1958, year_only_not_january_1=True)
    with pytest.raises(ValueError, match="Same-year"):
        same.benchmark()
    assert replace(same, same_year_death_before_62=True).benchmark() == (2020, True)


@pytest.mark.parametrize(
    "changes,match",
    [
        ({"no_prior_disability": False}, "authoritative"),
        ({"ordinary_non_windex": False}, "WINDEX"),
        ({"provenance": ""}, "provenance"),
        ({"death_year": 1969, "death_date": None}, "precede birth"),
        ({"worker_birth_year": 1969}, "disagree"),
        ({"death_year": 2019}, "disagree"),
        ({"authoritative_year": 1982}, "before 1983"),
    ],
)
def test_survivor_scope_and_benchmark_rejections(changes, match):
    with pytest.raises(ValueError, match=match):
        survivor_basis(**changes).benchmark()


def test_survivor_death_based_cola_origin_and_composite_ratio_once():
    event = ColaEvent("2020-12", "2021-01", D(".1"))
    record = survivor(
        monthly_amount=D(880), composite_ratio=D(".8"), valuation_month="2021-02"
    )
    result = compute(record, cola_events=[event])
    assert result.eligibility_pia_interval == (D(1000), D("1001.2"))
    assert row_for(result, "2026-01").cola_pia == 1100
    assert result.entitlement_total == 10560


@pytest.mark.parametrize(
    "field",
    [
        "nonbinding_rib_lim",
        "nonbinding_family_maximum",
        "no_dual_entitlement",
        "no_earnings_test_at_valuation",
    ],
)
def test_survivor_requires_every_identification_assertion(field):
    with pytest.raises(ValueError, match="Survivor inversion"):
        compute(survivor(**{field: False}))


@pytest.mark.parametrize(
    "changes",
    [
        {"composite_ratio": D(0)},
        {"composite_ratio": D(-1)},
        {"ratio_description": ""},
        {"monthly_amount": D(-1)},
        {"valuation_month": "2020-12"},
        {"monthly_amount": D("2000.5")},
        {"supplied_claiming_factor": D("1.2")},
    ],
)
def test_survivor_rejects_ambiguous_or_inconsistent_amount_and_ratio(changes):
    with pytest.raises(ValueError):
        compute(survivor(**changes))


@pytest.mark.parametrize(
    "flag,expected_pia", [(False, D("2048.0")), (True, D("2156.8"))]
)
@pytest.mark.parametrize("death_year", [2020, 2025])
def test_s770_pre2026_death_flag_changes_only_first_bend_increase(
    flag, expected_pia, death_year
):
    # M1 correction: factor-only gain .05*960=48; full raw gain
    # .1634*960=156.864, then initial-PIA dime truncation.
    record = survivor(
        survivor=survivor_basis(
            death_year=death_year, death_date=date(death_year, 8, 12)
        ),
        entitlement_month=f"{death_year}-09",
        valuation_month=f"{death_year}-11",
    )
    result = compute(
        record,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=flag,
    )
    assert row_for(result, "2026-01").eligibility_pia == expected_pia


def test_s770_post2025_death_before62_does_not_use_pre2026_flag():
    record = survivor(
        survivor=survivor_basis(death_year=2026, death_date=date(2026, 1, 15)),
        entitlement_month="2026-02",
        valuation_month="2026-04",
    )
    off = compute(
        record,
        2027,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=False,
    )
    on = compute(
        record,
        2027,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=True,
    )
    assert off.ledger == on.ledger
    assert row_for(off, "2027-01").eligibility_pia == D("2156.8")


def test_s770_death_after62_does_not_use_pre2026_death_before62_flag():
    record = survivor(
        survivor=survivor_basis(
            worker_birth_year=1950, worker_birth_date=date(1950, 6, 15)
        )
    )
    off = compute(
        record,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=False,
    )
    on = compute(
        record,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=True,
    )
    assert off.ledger == on.ledger
    assert row_for(off, "2026-01").eligibility_pia == D("2156.8")


@pytest.mark.parametrize(
    "flag,expected_pia,expected_cola,expected_payment",
    [
        (False, D("2048.0"), D("2341.3"), D(2060)),
        (True, D("2156.8"), D("2465.8"), D(2169)),
    ],
)
def test_survivor_other_levers_apply_independently_of_s770_flag(
    flag, expected_pia, expected_cola, expected_payment
):
    record = survivor(monthly_amount=D(2200))
    events = [
        ColaEvent("2020-12", "2021-01", D(".1")),
        ColaEvent("2025-12", "2026-01", D(".02")),
    ]
    policies = BenefitPolicies(
        cola_rates={"2021-01": D(".11"), "2026-01": D(".03")},
        across_the_board={2026: D(".1")},
        payable_share={2026: D(".8")},
    )
    result = compute(
        record,
        cola_events=events,
        policies=policies,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
        s770_survivor_bend_increase=flag,
    )
    row = row_for(result, "2026-01")
    assert row.eligibility_pia == expected_pia
    assert row.cola_pia == expected_cola
    assert row.payable_benefit == expected_payment


def test_sub_dollar_payment_exception_and_zero_survivor():
    record = retirement(pia=D(".9"), supplied_claiming_factor=D(1))
    assert row_for(compute(record), "2026-01").payable_benefit == D(".9")
    zero = compute(survivor(monthly_amount=D(0)))
    assert zero.entitlement_total == 0
    assert zero.eligibility_pia_interval == (D(0), D(".1"))


def test_historical_sub_dollar_entitlement_rejects_unmodeled_year_end_payments():
    # Before December 2006, SSA held sub-$1 benefits for manual year-end
    # payment. The restricted ledger cannot represent those as monthly checks.
    # https://secure.ssa.gov/poms.nsf/lnx/0300601020
    record = retirement(
        birth_date=date(1940, 1, 2),
        eligibility_year=2002,
        entitlement_month="2006-11",
        pia=D(".9"),
        supplied_claiming_factor=D(1),
    )
    with pytest.raises(ValueError, match="year-end manual payment timing"):
        compute(record, 2006)
    supported = compute(replace(record, entitlement_month="2006-12"), 2006)
    assert row_for(supported, "2006-12").payable_benefit == D(".9")
    assert supported.entitlement_total == D(".9")
    assert supported.payment_total == 0


def test_historical_sub_dollar_survivor_source_cannot_be_inverted_as_monthly_cash():
    record = survivor(
        birth_date=date(1940, 1, 2),
        survivor=survivor_basis(
            worker_birth_year=1950,
            worker_birth_date=date(1950, 6, 15),
            death_year=2005,
            death_date=date(2005, 8, 12),
        ),
        entitlement_month="2005-09",
        valuation_month="2006-12",
        monthly_amount=D(".9"),
    )
    with pytest.raises(ValueError, match="year-end manual payment timing"):
        compute(record)
    supported = compute(replace(record, valuation_month="2007-01"))
    assert supported.entitlement_total == D("10.8")


def test_historical_earnings_test_requires_explicit_no_trigger_assertion():
    # The earnings test before 2000 included ages and deduction rates that
    # differ from this route's modern FRA-based computation.
    record = retirement(
        birth_date=date(1933, 1, 2),
        eligibility_year=1995,
        entitlement_month="1999-01",
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    with pytest.raises(ValueError, match="Earnings testing before 2000"):
        compute(record, 1999)
    assert (
        compute(replace(record, earnings_test_no_trigger=True), 1999).entitlement_total
        == 12000
    )


@settings(max_examples=40, deadline=None)
@given(
    pia_dimes=st.integers(min_value=0, max_value=100_000),
    claim_month=st.integers(min_value=1, max_value=12),
)
def test_property_benefits_are_zero_before_entitlement(pia_dimes, claim_month):
    record = retirement(
        pia=D(pia_dimes) / 10,
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month=f"2026-{claim_month:02d}",
    )
    result = compute(record)
    assert all(
        row.payable_benefit == 0
        for row in result.ledger
        if row.entitlement_month < record.entitlement_month
    )


@settings(max_examples=40, deadline=None)
@given(
    monthly=st.integers(min_value=0, max_value=5000),
    annual_earnings=st.integers(min_value=0, max_value=500_000),
)
def test_property_earnings_test_never_exceeds_benefit(monthly, annual_earnings):
    record = retirement(
        pia=D(monthly),
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-01",
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    result = compute(
        record, earnings={2026: annual_earnings}, lower_exempt={2026: 24480}
    )
    assert D(0) <= result.earnings_test_reduction <= D(monthly * 12)
    assert all(
        D(0) <= row.earnings_test_reduction <= row.gross_benefit
        for row in result.ledger
    )
    assert all(row.payable_benefit >= 0 for row in result.ledger)


@settings(max_examples=50, deadline=None)
@given(
    pia_dimes=st.integers(min_value=100, max_value=100_000),
    ratio_hundredths=st.integers(min_value=50, max_value=150),
    rate_thousandths=st.integers(min_value=0, max_value=100),
)
def test_property_survivor_recovered_interval_reproduces_supplied_amount(
    pia_dimes, ratio_hundredths, rate_thousandths
):
    pia, ratio = D(pia_dimes) / 10, D(ratio_hundredths) / 100
    events = [ColaEvent("2020-12", "2021-01", D(rate_thousandths) / 1000)]
    current_pia = apply_colas(pia, 2020, "2025-01", events)
    supplied = D(int(current_pia * ratio))
    result = compute(
        survivor(monthly_amount=supplied, composite_ratio=ratio), cola_events=events
    )
    lower, upper = result.eligibility_pia_interval
    assert lower <= pia < upper
    assert D(int(apply_colas(lower, 2020, "2025-01", events) * ratio)) == supplied
    assert row_for(result, "2026-01").payable_benefit == supplied


def test_age_70_releases_deferred_credits_in_the_claim_calendar_year():
    # RS00615.690: claim-year credits become effective at age70 even before
    # the following January. Credits stop accruing when benefits commence.
    # https://secure.ssa.gov/poms.nsf/lnx/0300615690
    record = retirement(
        birth_date=date(1957, 9, 15),
        eligibility_year=2019,
        entitlement_month="2027-06",
        pia=D(1500),
    )
    result = compute(record, 2027)
    assert row_for(result, "2027-08").claiming_factor == D(1840) / D(1500)
    assert row_for(result, "2027-08").payable_benefit == 1840
    assert row_for(result, "2027-09").claiming_factor == D("1.26")
    assert row_for(result, "2027-09").payable_benefit == 1890
    assert row_for(compute(record, 2028), "2028-01").payable_benefit == 1890


def test_january_1_birth_uses_previous_cohort_fra_and_full_first_month():
    # The worker attains62 on December31,2021 but is first62 throughout
    # January2022. The1959 cohort gives FRA66y10m, attained October2026.
    # https://secure.ssa.gov/poms.nsf/lnx/0200302400
    # https://secure.ssa.gov/poms.nsf/lnx/0300201001
    record = retirement(
        birth_date=date(1960, 1, 1),
        eligibility_year=2021,
        entitlement_month="2022-01",
    )
    assert record.benchmark() == 2021
    assert full_retirement_age_months(record.birth_date) == 802
    assert claiming_factor(record.birth_date, "2026-10") == 1
    assert claiming_factor(record.birth_date, "2022-01") == Fraction(57, 80)
    assert compute(record, 2022).entitlement_total > 0
    with pytest.raises(ValueError, match="first eligible month"):
        compute(replace(record, entitlement_month="2021-12"), 2021)


def test_authoritative_survivor_year_does_not_require_fallback_birth_assumption():
    basis = survivor_basis(
        worker_birth_date=None,
        death_date=None,
        authoritative_year=2018,
        provenance="Authoritative computation year",
        no_prior_disability=False,
        year_only_not_january_1=False,
    )
    assert basis.benchmark() == (2018, True)
    assert compute(survivor(survivor=basis)).entitlement_total == 24_000


def test_exact_survivor_death_date_cannot_precede_birth_in_the_same_year():
    basis = survivor_basis(
        worker_birth_year=2020,
        worker_birth_date=date(2020, 5, 1),
        death_year=2020,
        death_date=date(2020, 4, 30),
    )
    with pytest.raises(ValueError, match="Death cannot precede birth"):
        basis.benchmark()


def test_survivor_entitlement_cannot_precede_known_death_month():
    record = survivor(entitlement_month="2020-07")
    with pytest.raises(ValueError, match="entitlement cannot precede"):
        compute(record)


def test_prior_year_earnings_test_does_not_require_older_earnings_history():
    # The record has been entitled since2022. January2026's check depends on
    # the2025 annual test, not on an unnecessary recursive read of2024/2023.
    record = retirement(
        pia=D(800),
        supplied_claiming_factor=D(1),
        earnings_test_no_trigger=False,
    )
    result = compute(
        record,
        2026,
        earnings={2025: 43_080, 2026: 0},
        lower_exempt={2025: 24_480, 2026: 24_480},
    )
    assert row_for(result, "2025-12").earnings_test_reduction == 500
    assert row_for(result, "2025-12").payable_benefit == 300
    assert result.entitlement_total == 9600
    assert result.payment_total == 9100


def test_claiming_dime_truncation_precedes_contributed_benefit_factor():
    # 1001.3*.7=700.91 ->700.9; then*1.1=770.99 ->770.
    # Multiplying the untruncated700.91 by1.1 would incorrectly pay771.
    record = retirement(pia=D("1001.3"), supplied_claiming_factor=D(".7"))
    result = compute(record, policies=BenefitPolicies(across_the_board={2026: D(".1")}))
    row = row_for(result, "2026-01")
    assert row.unrounded_benefit == D("700.91")
    assert row.gross_benefit == row.payable_benefit == 770


@pytest.mark.parametrize("source", ["aime", "pia"])
@settings(max_examples=15, deadline=None)
@given(scoring_year=st.integers(min_value=1983, max_value=2025))
def test_property_reform_before_benchmark_keeps_benefit_zero(source, scoring_year):
    record = retirement(
        source=source,
        aime=5000,
        birth_date=date(1964, 1, 2),
        eligibility_year=2026,
        entitlement_month="2026-01",
    )
    result = compute(
        record,
        scoring_year,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
    )
    assert result.entitlement_total == result.payment_total == 0
    assert all(row.payable_benefit == 0 for row in result.ledger)
    assert result.inferred_aime_interval is None


def test_s770_starts_with_january_entitlement_and_its_february_check():
    # Section2(c)(1) applies to benefits for months from January2026;
    # January's check still pays the unreformed December2025 entitlement.
    # https://www.congress.gov/bill/119th-congress/senate-bill/770/text
    record = retirement(
        source="aime",
        aime=5000,
        birth_date=date(1958, 1, 2),
        eligibility_year=2020,
        entitlement_month="2020-01",
        supplied_claiming_factor=D(1),
    )
    result = compute(
        record,
        formula_path=FormulaPath(s770=True),
        recompute_mode="retroactive",
    )
    december = row_for(result, "2025-12")
    january = row_for(result, "2026-01")
    assert december.payment_month == "2026-01"
    assert december.eligibility_pia == D("2156.8")
    assert december.payable_benefit == 2156
    assert january.payment_month == "2026-02"
    assert january.eligibility_pia == D("2313.6")
    assert january.payable_benefit == 2313
    assert result.payment_total == 27_599
    assert result.entitlement_total == 27_756


@pytest.mark.parametrize("birth", [date(2010, 1, 2), date(1970, 1, 2)])
def test_restricted_survivor_excludes_child_and_disabled_early_entitlement(birth):
    with pytest.raises(ValueError, match="restricted survivor route excludes"):
        compute(survivor(birth_date=birth))
