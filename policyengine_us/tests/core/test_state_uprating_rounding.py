"""Regression coverage for state parameter uprating and rounding."""

from math import isinf
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path
from types import SimpleNamespace

import pytest

from policyengine_core.parameters import Parameter, ParameterNode, load_parameter_file
from policyengine_us.parameters.uprating_extensions import (
    extend_vt_cpi_u_indexed_amounts,
    extend_wi_cpi_u_indexed_amounts,
    get_irs_cpi,
    round_wi_amount,
)
from policyengine_us.system import system as SYSTEM


PARAMETER_DIR = Path(__file__).parents[2] / "parameters"


def _thresholds(scale, period, bracket_indexes=(1, 2, 3)):
    return tuple(scale.brackets[index].threshold(period) for index in bracket_indexes)


def _observed_september_august_average(cpi, ending_year):
    """Average twelve actual monthly records without using an indexing helper."""
    months = [
        *(f"{ending_year - 1}-{month:02d}-01" for month in range(9, 13)),
        *(f"{ending_year}-{month:02d}-01" for month in range(1, 9)),
    ]
    observations = {
        value.instant_str: Decimal(str(value.value)) for value in cpi.values_list
    }
    # A missing month raises KeyError rather than silently completing the window.
    return sum(observations[month] for month in months) / Decimal(12)


def _wi_independent_indexed_amount(base, index, base_index, prior):
    """Apply the statutory ratio, $10 half-up rounding, and prior-year floor."""
    unrounded = Decimal(str(base)) * Decimal(str(index)) / Decimal(str(base_index))
    rounded = int(unrounded.quantize(Decimal("1E1"), rounding=ROUND_HALF_UP))
    return max(prior, rounded)


def _raw_state_indexing_parameters(*states, cpi=None):
    """Use published source trees so the extensions actually generate new years."""
    state_nodes = {
        state: SimpleNamespace(
            tax=SimpleNamespace(
                income=ParameterNode(
                    f"gov.states.{state}.tax.income",
                    directory_path=str(
                        PARAMETER_DIR / f"gov/states/{state}/tax/income"
                    ),
                )
            )
        )
        for state in states
    }
    return SimpleNamespace(
        gov=SimpleNamespace(
            bls=SimpleNamespace(
                cpi=SYSTEM.parameters.gov.bls.cpi.clone() if cpi is None else cpi
            ),
            states=SimpleNamespace(**state_nodes),
        )
    )


def _indexed_state_values(parameters, years):
    indexed = []
    states = parameters.gov.states
    if hasattr(states, "vt"):
        tax = states.vt.tax.income
        standard = tax.deductions.standard
        indexed.extend(standard.base.children.values())
        indexed.extend((standard.additional, tax.exemption.personal))
        for status in (
            "single",
            "head_of_household",
            "joint",
            "surviving_spouse",
            "separate",
        ):
            scale = getattr(tax.rates, status)
            indexed.extend(bracket.threshold for bracket in scale.brackets[1:])
    if hasattr(states, "wi"):
        indexed.extend(
            parameter
            for parameter in states.wi.tax.income.get_descendants()
            if isinstance(parameter, Parameter)
            and parameter.metadata.get("wisconsin_indexing")
        )
    return {
        (parameter.name, year): parameter(f"{year}-01-01")
        for parameter in indexed
        for year in years
    }


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
    uprating = SYSTEM.parameters.gov.irs.uprating
    factor = Decimal(str(uprating("2027-01-01"))) / Decimal(str(uprating("2026-01-01")))
    expected_threshold = int(
        (Decimal(30_000) * factor).quantize(Decimal("1E1"), rounding=ROUND_FLOOR)
    )

    assert scale.brackets[1].threshold("2026-01-01") == 30_000
    assert scale.brackets[1].threshold("2027-01-01") == expected_threshold
    assert scale.brackets[1].rate("2027-01-01") == pytest.approx(0.0521)
    assert scale.brackets[2].rate("2027-01-01") == pytest.approx(0.06)


def test_vt_deductions_and_exemption_preserve_published_2025():
    # 2025 Vermont Income Tax Return Booklet, p. 11, and IN-111 line 5e.
    standard = SYSTEM.parameters.gov.states.vt.tax.income.deductions.standard
    base = standard.base("2025-01-01")

    assert standard.additional("2025-01-01") == 1_250
    expected = {
        "JOINT": 15_300,
        "HEAD_OF_HOUSEHOLD": 11_450,
        "SURVIVING_SPOUSE": 15_300,
        "SINGLE": 7_650,
        "SEPARATE": 7_650,
    }
    assert {status: base[status] for status in expected} == expected
    assert (
        SYSTEM.parameters.gov.states.vt.tax.income.exemption.personal("2025-01-01")
        == 5_300
    )


def test_vt_2026_deductions_and_exemption_use_observed_unchained_cpi():
    # These 2026 amounts are calculated estimates pending Vermont publication.
    # 32 V.S.A. 5811(21)(C)-(D): $6,000/$9,000/$12,000 standard deductions,
    # $1,000 additional deduction, and $4,150 exemption. The 2017 base window
    # reproduces published amounts; each increase rounds down to $50.
    nsa = load_parameter_file(str(PARAMETER_DIR / "gov/bls/cpi/cpi_u_nsa.yaml"))
    numerator = _observed_september_august_average(nsa, 2025)
    denominator = _observed_september_august_average(nsa, 2017)
    assert float(numerator) == pytest.approx(319.205)
    assert float(denominator) == pytest.approx(243.391833333333)
    cola = numerator / denominator - 1

    def expected_amount(statutory_base):
        increase = (Decimal(statutory_base) * cola / 50).to_integral_value(
            rounding=ROUND_FLOOR
        ) * 50
        return statutory_base + int(increase)

    tax = SYSTEM.parameters.gov.states.vt.tax.income
    base = tax.deductions.standard.base("2026-01-01")
    for status, statutory_base in (
        ("SINGLE", 6_000),
        ("SEPARATE", 6_000),
        ("HEAD_OF_HOUSEHOLD", 9_000),
        ("JOINT", 12_000),
        ("SURVIVING_SPOUSE", 12_000),
    ):
        assert base[status] == expected_amount(statutory_base), status
    assert tax.deductions.standard.additional("2026-01-01") == expected_amount(1_000)
    assert tax.exemption.personal("2026-01-01") == expected_amount(4_150)


@pytest.mark.parametrize(
    ("filing_status", "expected"),
    (
        ("head_of_household", (68_000, 175_500, 284_150)),
        ("joint", (84_700, 204_750, 312_050)),
        ("separate", (42_350, 102_375, 156_025)),
        ("single", (50_750, 122_850, 256_300)),
        ("surviving_spouse", (84_700, 204_750, 312_050)),
    ),
)
def test_vt_income_tax_thresholds_preserve_published_preliminary_2026(
    filing_status,
    expected,
):
    # IN-114-Instr-2026, p. 2, explicitly labels these rates preliminary.
    # MFS thresholds use $25 increments, as §1(f)(7)(B) prescribes.
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
def test_wi_standard_deduction_phase_out_thresholds_preserve_published_2026(
    filing_status,
    published_2026,
):
    # 2026 Form 1-ES instructions, p. 2, Standard Deduction Schedules.
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


def test_wi_standard_deduction_maxima_and_crossover_preserve_published_2026():
    # 2026 Form 1-ES instructions, p. 2, including the HOH switch to single.
    standard = SYSTEM.parameters.gov.states.wi.tax.income.deductions.standard
    maxima = standard.max("2026-01-01")
    expected = {
        "SINGLE": 13_960,
        "HEAD_OF_HOUSEHOLD": 18_030,
        "JOINT": 25_840,
        "SURVIVING_SPOUSE": 25_840,
        "SEPARATE": 12_280,
    }
    assert {status: maxima[status] for status in expected} == expected
    assert (
        standard.phase_out.head_of_household.brackets[2].threshold("2026-01-01")
        == 58_827
    )


@pytest.mark.parametrize(
    ("filing_status", "published_2026", "statutory_2025"),
    (
        ("head_of_household", (15_110, 51_950, 332_720), (14_680, 50_480, 323_290)),
        ("joint", (20_150, 69_260, 443_630), (19_580, 67_300, 431_060)),
        ("separate", (10_080, 34_630, 221_820), (9_790, 33_650, 215_530)),
        ("single", (15_110, 51_950, 332_720), (14_680, 50_480, 323_290)),
    ),
)
def test_wi_income_tax_thresholds_use_published_then_rounded_values(
    filing_status,
    published_2026,
    statutory_2025,
):
    # Published 2026: Form 1-ES instructions, p. 3. 2027: Wis. Stat.
    # 71.06(1r), (2)(k)-(L), (2e)(bm) and (c), using Act 15's 2025 bases
    # and actual prior-August CUUR0000SA0. Later August forecasts are proxies.
    scale = getattr(
        SYSTEM.parameters.gov.states.wi.tax.income.rates,
        filing_status,
    )

    assert _thresholds(scale, "2026-01-01") == published_2026
    nsa = SYSTEM.parameters.gov.bls.cpi.cpi_u_nsa
    assert nsa("2024-08-01") == 314.796
    assert nsa("2026-08-01") == 334.980
    expected_2027 = tuple(
        _wi_independent_indexed_amount(base, "334.980", "314.796", prior)
        for base, prior in zip(statutory_2025, published_2026)
    )
    assert _thresholds(scale, "2027-01-01") == expected_2027


def test_state_indexes_do_not_follow_federal_chained_cpi():
    baseline = _raw_state_indexing_parameters("vt", "wi")
    refreshed = _raw_state_indexing_parameters("vt", "wi")
    refreshed.gov.bls.cpi.c_cpi_u.update(period="month:2026-08-01:1", value=9_999)
    assert get_irs_cpi(refreshed, 2026) != get_irs_cpi(baseline, 2026)

    for parameters in (baseline, refreshed):
        extend_vt_cpi_u_indexed_amounts(parameters, 2028)
        extend_wi_cpi_u_indexed_amounts(parameters, 2028)
    # 2026 and 2027 have NSA observations; Vermont's 2027 window still
    # estimates the missing October 2025 value. 2028 uses the documented
    # unchained state forecast proxies, which must also be independent.
    assert _indexed_state_values(refreshed, (2026, 2027, 2028)) == (
        _indexed_state_values(baseline, (2026, 2027, 2028))
    )


@pytest.mark.parametrize(
    ("amount", "expected"),
    (
        ("4.999", 0),
        ("5", 10),
        ("15", 20),
        ("25", 30),
        ("1004.999", 1_000),
        ("1005", 1_010),
    ),
)
def test_wi_half_ten_rounds_up(amount, expected):
    assert round_wi_amount(Decimal(amount)) == expected


def test_wi_indexed_amounts_never_decrease():
    nsa = Parameter(
        "cpi_u_nsa",
        data={
            "1999-08-01": 167.1,
            "2015-08-01": 238.316,
            "2024-08-01": 314.796,
            "2025-08-01": 323.976,
            "2026-08-01": 300,
            "2027-08-01": 290,
        },
    )
    parameters = _raw_state_indexing_parameters(
        "wi", cpi=SimpleNamespace(cpi_u_nsa=nsa)
    )
    indexed = [
        parameter
        for parameter in parameters.gov.states.wi.tax.income.get_descendants()
        if isinstance(parameter, Parameter)
        and "base" in parameter.metadata.get("wisconsin_indexing", {})
    ]
    assert indexed
    published = {parameter.name: parameter("2026-01-01") for parameter in indexed}
    assert nsa("2027-08-01") < nsa("2026-08-01") < nsa("2025-08-01")
    extend_wi_cpi_u_indexed_amounts(parameters, 2028)

    for parameter in indexed:
        rule = parameter.metadata["wisconsin_indexing"]
        base_index = nsa(f"{rule['base_year']}-08-01")
        prior = published[parameter.name]
        for year in (2027, 2028):
            current_index = nsa(f"{year - 1}-08-01")
            unrounded = (
                Decimal(str(rule["base"]))
                * Decimal(str(current_index))
                / Decimal(str(base_index))
            )
            # Every statutory candidate falls below its published anchor,
            # so equality proves that the no-decrease clause actually binds.
            assert unrounded < prior, (parameter.name, year)
            assert parameter(f"{year}-01-01") == prior, (parameter.name, year)


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
