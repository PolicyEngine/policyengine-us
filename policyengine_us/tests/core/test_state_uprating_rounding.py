"""Regression coverage for state parameter uprating and rounding."""

from math import isinf

import pytest

from policyengine_us import CountryTaxBenefitSystem


SYSTEM = CountryTaxBenefitSystem()


def _thresholds(scale, period, bracket_indexes=(1, 2, 3)):
    return tuple(scale.brackets[index].threshold(period) for index in bracket_indexes)


def test_ar_income_tax_thresholds_round_down_after_last_published_year():
    scale = SYSTEM.parameters.gov.states.ar.tax.income.rates.main.rate

    assert _thresholds(scale, "2027-01-01", (1, 2, 3, 4)) == (
        5_700,
        11_500,
        16_400,
        27_100,
    )
    assert isinf(scale.brackets[5].threshold("2027-01-01"))
    assert isinf(scale.brackets[6].threshold("2027-01-01"))


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
    ("filing_status", "expected"),
    (
        ("head_of_household", 19_990),
        ("joint", 28_850),
        ("separate", 13_690),
        ("single", 19_990),
    ),
)
def test_wi_standard_deduction_phase_out_thresholds_round_to_ten_dollars(
    filing_status,
    expected,
):
    scale = getattr(
        SYSTEM.parameters.gov.states.wi.tax.income.deductions.standard.phase_out,
        filing_status,
    )

    assert scale.brackets[1].threshold("2026-01-01") == expected


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
