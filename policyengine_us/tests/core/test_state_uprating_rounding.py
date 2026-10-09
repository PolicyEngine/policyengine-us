"""Regression coverage for state parameter uprating and rounding."""

from math import isinf

import pytest

from policyengine_us.system import system as SYSTEM


def _thresholds(scale, period, bracket_indexes=(1, 2, 3)):
    return tuple(scale.brackets[index].threshold(period) for index in bracket_indexes)


def test_ar_income_tax_bounds_round_to_nearest_100_after_last_published_year():
    # A.C.A. 26-51-201(d)(1): bracket amounts are indexed "rounding to the
    # nearest one hundred dollars ($100)". Expected values follow the loaded
    # index, so a CPI refresh moves them without breaking the test.
    main = SYSTEM.parameters.gov.states.ar.tax.income.rates.main
    uprating = SYSTEM.parameters.gov.irs.uprating
    high_income = main.high_income
    bounds_2026 = {
        "rate": (main.rate, (1, 2, 3, 4), (5_600, 11_200, 16_000, 26_400)),
        "high-income threshold": (None, None, (94_700,)),
        "(B) 2% row top": (high_income.rate, (1,), (4_700,)),
        "(C) rows": (
            high_income.bracket_adjustment,
            tuple(range(30)),
            tuple(range(94_700, 97_601, 100)),
        ),
    }
    differs_from_rounding_down = False
    for year in range(2027, 2036):
        period = f"{year}-01-01"
        factor = uprating(period) / uprating("2026-01-01")
        for name, (scale, indexes, bases) in bounds_2026.items():
            if scale is None:
                loaded = (high_income.threshold(period),)
            else:
                loaded = _thresholds(scale, period, indexes)
            expected = tuple(round(base * factor / 100) * 100 for base in bases)
            assert loaded == expected, (year, name)
            rounded_down = tuple(base * factor // 100 * 100 for base in bases)
            differs_from_rounding_down |= loaded != rounded_down
        assert isinf(main.rate.brackets[5].threshold(period))
        assert isinf(main.rate.brackets[6].threshold(period))
    # With 2027's factor, 5,600 x 1.0298 = 5,766.9 rounds up to 5,800.
    assert differs_from_rounding_down


def test_nm_low_income_rebate_amounts_round_to_whole_dollars():
    amount = SYSTEM.parameters.gov.states.nm.tax.income.rebates.low_income.amount
    exemption_names = (
        "one_exemption",
        "two_exemptions",
        "three_exemptions",
        "four_exemptions",
        "five_exemptions",
        "six_exemptions",
    )
    projected_amounts = []

    for exemption_name in exemption_names:
        scale = getattr(amount, exemption_name)
        for bracket in scale.brackets:
            uprating = bracket.amount.metadata.get("uprating")
            if isinstance(uprating, dict) and "rounding" in uprating:
                projected_amounts.append(bracket.amount("2026-01-01"))

    assert len(projected_amounts) == 121
    assert all(value == round(value) for value in projected_amounts)
    assert amount.one_exemption.brackets[0].amount("2026-01-01") == 229
    assert amount.five_exemptions.brackets[0].amount("2026-01-01") == 534


def test_or_dependent_standard_deduction_uses_published_then_rounded_values():
    minimum = getattr(
        SYSTEM.parameters.gov.states, "or"
    ).tax.income.deductions.standard.claimable_as_dependent.min

    assert minimum("2025-01-01") == 1_350
    assert minimum("2026-01-01") == 1_350
    assert minimum("2027-01-01") == 1_400


def test_sc_dependent_deductions_round_down_to_ten_dollars():
    parameters = SYSTEM.parameters
    baseline = parameters.gov.states.sc.tax.income.deductions.dependent_exemption.amount
    contributed = parameters.gov.contrib.states.sc.dependent_exemption.amount
    young_child = parameters.gov.states.sc.tax.income.deductions.young_child.amount

    assert baseline("2026-01-01") == 5_040
    assert contributed("2026-01-01") == 5_040
    assert young_child("2026-01-01") == 5_040


def test_sc_income_tax_rounding_applies_to_threshold_not_rates():
    scale = SYSTEM.parameters.gov.states.sc.tax.income.rates

    assert scale.brackets[1].threshold("2027-01-01") == 30_890
    assert scale.brackets[1].rate("2027-01-01") == pytest.approx(0.0521)
    assert scale.brackets[2].rate("2027-01-01") == pytest.approx(0.06)


def test_vt_standard_deductions_round_down_to_fifty_dollars():
    standard = SYSTEM.parameters.gov.states.vt.tax.income.deductions.standard
    base = standard.base("2026-01-01")

    assert standard.additional("2026-01-01") == 1_250
    expected = {
        "JOINT": 15_600,
        "HEAD_OF_HOUSEHOLD": 11_700,
        "SURVIVING_SPOUSE": 15_600,
        "SINGLE": 7_800,
        "SEPARATE": 7_800,
    }
    assert {status: base[status] for status in expected} == expected


@pytest.mark.parametrize(
    ("filing_status", "expected"),
    (
        ("head_of_household", (67_700, 174_850, 283_100)),
        ("joint", (84_350, 203_950, 310_850)),
        ("separate", (42_150, 101_950, 155_400)),
        ("single", (50_500, 122_400, 255_350)),
        ("surviving_spouse", (84_350, 203_950, 310_850)),
    ),
)
def test_vt_income_tax_thresholds_round_down_to_fifty_dollars(
    filing_status,
    expected,
):
    scale = getattr(
        SYSTEM.parameters.gov.states.vt.tax.income.rates,
        filing_status,
    )

    assert _thresholds(scale, "2026-01-01") == expected


@pytest.mark.parametrize(
    ("filing_status", "published_2026"),
    (
        # 2026 Form 1-ES instructions, 2026 Standard Deduction schedules.
        ("head_of_household", 20_120),
        ("joint", 29_040),
        ("separate", 13_780),
        ("single", 20_120),
    ),
)
def test_wi_standard_deduction_phase_out_thresholds_round_to_ten_dollars(
    filing_status,
    published_2026,
):
    scale = getattr(
        SYSTEM.parameters.gov.states.wi.tax.income.deductions.standard.phase_out,
        filing_status,
    )
    uprating = SYSTEM.parameters.gov.irs.uprating

    assert scale.brackets[1].threshold("2026-01-01") == published_2026
    # Later years project from the published 2026 start, rounded to the
    # nearest $10. Expected values follow the loaded index.
    factor = uprating("2027-01-01") / uprating("2026-01-01")
    expected_2027 = round(published_2026 * factor / 10) * 10
    assert scale.brackets[1].threshold("2027-01-01") == expected_2027


@pytest.mark.parametrize(
    ("filing_status", "published_2026", "projected_2027"),
    (
        ("head_of_household", (15_110, 51_950, 332_720), (15_560, 53_500, 342_640)),
        ("joint", (20_150, 69_260, 443_630), (20_750, 71_320, 456_850)),
        ("separate", (10_080, 34_630, 221_820), (10_380, 35_660, 228_430)),
        ("single", (15_110, 51_950, 332_720), (15_560, 53_500, 342_640)),
    ),
)
def test_wi_income_tax_thresholds_use_published_then_rounded_values(
    filing_status,
    published_2026,
    projected_2027,
):
    scale = getattr(
        SYSTEM.parameters.gov.states.wi.tax.income.rates,
        filing_status,
    )

    assert _thresholds(scale, "2026-01-01") == published_2026
    assert _thresholds(scale, "2027-01-01") == projected_2027


def test_wa_working_families_tax_credit_amounts_round_to_five_dollars():
    scale = SYSTEM.parameters.gov.states.wa.tax.income.credits.working_families_tax_credit.amount

    assert tuple(bracket.amount("2026-01-01") for bracket in scale.brackets) == (
        345,
        675,
        1_020,
        1_360,
    )


def test_wa_millionaires_standard_deduction_uses_biennial_schedule():
    deduction = (
        SYSTEM.parameters.gov.states.wa.tax.income.millionaires_tax.deductions.standard
    )

    assert tuple(deduction(f"{year}-01-01") for year in range(2028, 2036)) == (
        1_000_000,
        1_000_000,
        1_023_000,
        1_023_000,
        1_046_000,
        1_046_000,
        1_070_000,
        1_070_000,
    )


def test_me_standard_deductions_published_2026():
    standard = SYSTEM.parameters.gov.states.me.tax.income.deductions.standard
    base = standard.amount("2026-01-01")
    aged_or_blind = standard.aged_or_blind("2026-01-01")

    expected_base = {
        "SINGLE": 15_700,
        "JOINT": 31_400,
        "SEPARATE": 15_700,
        "HEAD_OF_HOUSEHOLD": 23_550,
        "SURVIVING_SPOUSE": 31_400,
    }
    assert {status: base[status] for status in expected_base} == expected_base

    expected_additional = {
        "SINGLE": 2_050,
        "JOINT": 1_650,
        "SEPARATE": 1_650,
        "HEAD_OF_HOUSEHOLD": 2_050,
        "SURVIVING_SPOUSE": 1_650,
    }
    assert {
        status: aged_or_blind[status] for status in expected_additional
    } == expected_additional


def test_mn_alternate_deduction_reductions_round_down_to_fifty_dollars():
    deductions = SYSTEM.parameters.gov.states.mn.tax.income.deductions
    itemized = deductions.itemized.reduction.alternate.income_threshold("2026-01-01")
    standard = deductions.standard.reduction.alternate.income_threshold("2026-01-01")

    assert itemized == 1_107_750
    assert standard == 1_107_750


def test_mn_marriage_credit_thresholds_use_published_2025():
    marriage = SYSTEM.parameters.gov.states.mn.tax.income.credits.marriage

    assert marriage.minimum_individual_income("2025-01-01") == 31_000
    assert marriage.minimum_taxable_income("2025-01-01") == 48_000


def test_mt_old_age_subtraction_uses_published_2025():
    amount = SYSTEM.parameters.gov.states.mt.tax.income.subtractions.old_age.amount

    assert amount.brackets[0].amount("2025-01-01") == 0
    assert amount.brackets[1].amount("2024-01-01") == 5_500
    assert amount.brackets[1].amount("2025-01-01") == 5_660


AZ_STANDARD_DEDUCTION_STATUSES = ("SINGLE", "SEPARATE", "HEAD_OF_HOUSEHOLD")


@pytest.mark.parametrize("status", AZ_STANDARD_DEDUCTION_STATUSES)
def test_az_standard_deduction_is_indexed_like_the_federal_basic_amount(status):
    # A.R.S. 43-1041(H): the subsection A amounts are adjusted "in the same
    # manner in which the federal basic standard deduction is adjusted for
    # inflation pursuant to section 63". Laws 2026, ch. 140 set those amounts
    # to the federal 2025 amounts, so under current law the Arizona amounts
    # equal the federal ones in every later year. A parent-level uprating key
    # used to leave Arizona at its 2025 amounts from 2026 on. After 2026 this
    # checks the model's projection, which uprates the rounded 2026 amount.
    arizona = getattr(
        SYSTEM.parameters.gov.states.az.tax.income.deductions.standard.amount, status
    )
    federal = getattr(SYSTEM.parameters.gov.irs.deductions.standard.amount, status)
    uprating = SYSTEM.parameters.gov.irs.uprating
    base_2026 = arizona("2026-01-01")
    previous = arizona("2025-01-01")
    for year in range(2025, 2036):
        period = f"{year}-01-01"
        amount = arizona(period)
        assert amount == federal(period), (status, year)
        assert amount >= previous, (status, year)
        previous = amount
        if year > 2026:
            # 26 U.S.C. 63(c)(7)(B)(ii): round increases down to a multiple
            # of $50.
            factor = uprating(period) / uprating("2026-01-01")
            assert amount == base_2026 * factor // 50 * 50, (status, year)
    assert arizona("2035-01-01") > base_2026


def test_az_joint_standard_deduction_is_twice_the_single_amount():
    # 26 U.S.C. 63(c)(2)(A): the federal basic standard deduction for a joint
    # return is 200% of the single amount, so the Arizona joint amount,
    # indexed in the same manner, is twice the Arizona single amount.
    amount = SYSTEM.parameters.gov.states.az.tax.income.deductions.standard.amount
    for year in range(2025, 2036):
        period = f"{year}-01-01"
        assert amount.JOINT(period) == 2 * amount.SINGLE(period), year
