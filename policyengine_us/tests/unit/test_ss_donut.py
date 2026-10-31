"""Pure annual donut coverage and independently named parameter variants."""

from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from hypothesis import given, strategies as st
from policyengine_core.parameters import ParameterNode
import pytest

import policyengine_us
from policyengine_us.tools.social_security.donut import (
    DONUT_VARIANTS,
    DonutParameters,
    compute_donut_year,
    donut_parameters_at,
)


P = DonutParameters(
    in_effect=True,
    threshold=400000,
    tax_rate=".124",
    credit_enabled=True,
    credit_rate=".02",
)


def _parameters():
    root = ParameterNode(data={})
    parent = root
    for name in ("gov", "contrib", "ssa", "history"):
        child = ParameterNode(name, data={})
        parent.add_child(name, child)
        parent = child
    path = (
        Path(policyengine_us.__file__).resolve().parent
        / "parameters/gov/contrib/ssa/history/donut"
    )
    parent.add_child("donut", ParameterNode("donut", directory_path=str(path)))
    return root


@pytest.mark.parametrize("year", [1951, 1980])
@pytest.mark.parametrize("variant", DONUT_VARIANTS)
def test_all_off_donut_parameters_accept_pre1983_earnings_years(year, variant):
    # Eligibility benchmarks start in 1983, while covered-earnings histories
    # start in 1951. Read every scalar from the real authored Core subtree:
    # an eligibility-dated default would fail before annual activation checks.
    parameters = _parameters()
    settings = donut_parameters_at(parameters, year, variant)
    assert settings.in_effect is False
    result = compute_donut_year(
        year, covered_wages=500800, ordinary_cap=120000, parameters=settings
    )
    assert result.taxed_earnings == result.credited_earnings == result.tax == 0


@pytest.mark.parametrize(
    "wages,expected",
    [
        (0, 0),
        (120000, 0),
        (120001, 0),
        (399999, 0),
        (400000, 0),
        (400001, 1),
        (500800, 100800),
    ],
)
def test_cap_gap_and_threshold_boundaries(wages, expected):
    result = compute_donut_year(
        2038, covered_wages=wages, ordinary_cap=120000, parameters=P
    )
    assert result.taxed_earnings == expected
    assert result.credited_earnings == expected
    assert result.tax == expected * Fraction(".124")


def test_cap_overtaking_fixed_threshold_leaves_no_double_counted_tier():
    result = compute_donut_year(
        2059, covered_wages=500800, ordinary_cap=450000, parameters=P
    )
    assert result.threshold == 450000
    assert result.taxed_earnings == 50800


@pytest.mark.parametrize(
    "settings,year",
    [(replace(P, in_effect=False), 2038), (P, 2026), (replace(P, tax_rate=0), 2038)],
)
def test_disabled_pre_activation_and_untaxed_earnings_receive_no_credit(settings, year):
    result = compute_donut_year(
        year, covered_wages=500800, ordinary_cap=120000, parameters=settings
    )
    assert result.taxed_earnings == result.credited_earnings == result.tax == 0


def test_no_credit_variant_keeps_taxed_earnings_separate():
    result = compute_donut_year(
        2038,
        covered_wages=500800,
        ordinary_cap=120000,
        parameters=replace(P, credit_enabled=False),
    )
    assert result.taxed_earnings == 100800
    assert result.credited_earnings == 0
    assert result.tax == Fraction("12499.20")


@pytest.mark.parametrize(
    "include_se,include_draw,expected",
    [
        (False, False, 0),
        (True, False, 10000),
        (False, True, 20000),
        (True, True, 40000),
    ],
)
def test_coverage_flags_apply_identically_for_tax_and_credit(
    include_se, include_draw, expected
):
    result = compute_donut_year(
        2038,
        covered_wages=390000,
        existing_covered_se=20000,
        owners_draw_net_earnings=30000,
        ordinary_cap=120000,
        parameters=replace(
            P, include_self_employment=include_se, include_owners_draw=include_draw
        ),
    )
    assert result.taxed_earnings == result.credited_earnings == expected


def test_net_draw_and_existing_se_are_counted_once():
    result = compute_donut_year(
        2038,
        covered_wages=350000,
        existing_covered_se=20000,
        owners_draw_net_earnings=55410,
        ordinary_cap=120000,
        parameters=P,
    )
    assert result.taxed_earnings == result.credited_earnings == 25410


@given(wages=st.integers(min_value=120001, max_value=400000))
def test_donut_never_credits_the_gap(wages):
    result = compute_donut_year(
        2038, covered_wages=wages, ordinary_cap=120000, parameters=P
    )
    assert result.taxed_earnings == result.credited_earnings == 0


@pytest.mark.parametrize(
    "field",
    [
        "covered_wages",
        "existing_covered_se",
        "owners_draw_net_earnings",
        "ordinary_cap",
    ],
)
def test_negative_covered_inputs_rejected(field):
    arguments = {"covered_wages": 500800, "ordinary_cap": 120000, field: -1}
    with pytest.raises(ValueError, match="nonnegative"):
        compute_donut_year(2038, parameters=P, **arguments)


@pytest.mark.parametrize("year", [2027, 2036, 2038, 2054, 2057, 2059])
def test_oact_variants_remain_separate_and_fixed_threshold_through_claim_horizon(year):
    parameters = _parameters()
    high = donut_parameters_at(parameters, year, "oact_2025_e2_13")
    low = donut_parameters_at(parameters, year, "oact_2025_e2_14")
    assert high.in_effect is low.in_effect is False
    assert high.threshold == 400000
    assert low.threshold == 250000
    assert high.start_year == low.start_year == 2027
    assert high.tax_rate == low.tax_rate == 0.124
    assert high.credit_rate == low.credit_rate == 0.02
    assert high.credit_enabled is low.credit_enabled is True
    assert high.include_self_employment is low.include_self_employment is True


def test_named_credit_and_no_credit_variants_can_coexist():
    parameters = _parameters()
    variants = parameters.gov.contrib.ssa.history.donut
    variants.oact_2025_e2_13.in_effect.update(start="2027-01-01", value=True)
    variants.oact_2025_e2_14.in_effect.update(start="2027-01-01", value=True)
    variants.oact_2025_e2_14.credit_enabled.update(start="2027-01-01", value=False)
    high = compute_donut_year(
        2038,
        covered_wages=500800,
        ordinary_cap=120000,
        parameters=donut_parameters_at(parameters, 2038, "oact_2025_e2_13"),
    )
    low = compute_donut_year(
        2038,
        covered_wages=500800,
        ordinary_cap=120000,
        parameters=donut_parameters_at(parameters, 2038, "oact_2025_e2_14"),
    )
    assert high.taxed_earnings == high.credited_earnings == 100800
    assert low.taxed_earnings == 250800
    assert low.credited_earnings == 0


def test_custom_variant_defaults_are_neutral_and_accept_a_dated_threshold():
    parameters = _parameters()
    settings = parameters.gov.contrib.ssa.history.donut.custom
    settings.in_effect.update(start="2027-01-01", value=True)
    settings.tax_rate.update(start="2027-01-01", value=0.1)
    settings.threshold.update(start="2027-01-01", value=500000)
    settings.threshold.update(start="2030-01-01", value=600000)
    assert donut_parameters_at(parameters, 2029, "custom").threshold == 500000
    assert donut_parameters_at(parameters, 2030, "custom").threshold == 600000
    assert donut_parameters_at(parameters, 2038, "custom").credit_enabled is False
    with pytest.raises(ValueError, match="Unknown donut variant"):
        donut_parameters_at(parameters, 2038, "unknown")
    assert len(DONUT_VARIANTS) == 3
