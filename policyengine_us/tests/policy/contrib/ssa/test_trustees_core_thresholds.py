import math

import pytest

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.parameters.uprating_extensions import (
    round_social_security_payroll_cap,
)
from policyengine_us.reforms.ssa.trustees_2025 import (
    TRUSTEES_2025_AVERAGE_WAGE_GROWTH_PCT,
    TRUSTEES_2025_NAWI_ASSUMPTION,
)
from policyengine_us.reforms.ssa.trustees_core_thresholds import (
    TRUSTEES_CORE_THRESHOLD_ASSUMPTION,
    create_trustees_core_thresholds_reform,
)


def _parameters(reform=None):
    return CountryTaxBenefitSystem(reform=reform).parameters


def test_metadata_marks_trustees_core_thresholds_as_explicit_assumption():
    assert (
        TRUSTEES_CORE_THRESHOLD_ASSUMPTION["name"] == "trustees-2025-core-thresholds-v1"
    )
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["not_default_current_law"] is True
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["start_year"] == 2035
    assert (
        TRUSTEES_CORE_THRESHOLD_ASSUMPTION["economic_assumption"]
        == TRUSTEES_2025_NAWI_ASSUMPTION["name"]
    )
    assert "amt_thresholds" in TRUSTEES_CORE_THRESHOLD_ASSUMPTION["parameter_groups"]


def test_reform_applies_trustees_2025_nawi_path():
    baseline = _parameters()
    reformed = _parameters((create_trustees_core_thresholds_reform(),))

    baseline_nawi = baseline.gov.ssa.nawi
    reformed_nawi = reformed.gov.ssa.nawi

    assert reformed_nawi("2033-01-01") == baseline_nawi("2033-01-01")
    for year in [2034, 2035, 2040, 2100]:
        growth = float(reformed_nawi(f"{year}-01-01")) / float(
            reformed_nawi(f"{year - 1}-01-01")
        )
        expected_growth = 1 + TRUSTEES_2025_AVERAGE_WAGE_GROWTH_PCT[year] / 100
        assert growth == pytest.approx(expected_growth)


def test_reform_recomputes_payroll_cap_from_trustees_2025_nawi_path():
    reformed = _parameters((create_trustees_core_thresholds_reform(),))
    nawi = reformed.gov.ssa.nawi
    payroll_cap = reformed.gov.irs.payroll.social_security.cap

    for year in [2036, 2040, 2100]:
        current_cap = payroll_cap(f"{year - 1}-01-01")
        expected_cap = round_social_security_payroll_cap(
            current_cap * nawi(f"{year - 2}-01-01") / nawi(f"{year - 3}-01-01")
        )
        assert payroll_cap(f"{year}-01-01") == expected_cap


def test_reform_wage_indexes_core_tax_threshold_from_2035():
    baseline = _parameters()
    reformed = _parameters((create_trustees_core_thresholds_reform(),))

    baseline_threshold = baseline.gov.irs.income.bracket.thresholds.children["1"].SINGLE
    reformed_threshold = reformed.gov.irs.income.bracket.thresholds.children["1"].SINGLE
    nawi = reformed.gov.ssa.nawi

    assert reformed_threshold("2034-01-01") == baseline_threshold("2034-01-01")
    nawi_growth = float(nawi("2034-01-01")) / float(nawi("2033-01-01"))
    expected_2035 = (
        math.floor(float(reformed_threshold("2034-01-01")) * nawi_growth / 25) * 25
    )
    assert reformed_threshold("2035-01-01") == expected_2035
    assert reformed_threshold("2035-01-01") != baseline_threshold("2035-01-01")


def test_reform_updates_standard_deduction_and_amt_thresholds():
    baseline = _parameters()
    reformed = _parameters((create_trustees_core_thresholds_reform(),))

    standard_deduction = reformed.gov.irs.deductions.standard.amount.SINGLE
    amt_bracket = reformed.gov.irs.income.amt.brackets[1].threshold

    assert standard_deduction(
        "2034-01-01"
    ) == baseline.gov.irs.deductions.standard.amount.SINGLE("2034-01-01")
    assert amt_bracket("2034-01-01") == baseline.gov.irs.income.amt.brackets[
        1
    ].threshold("2034-01-01")
    assert standard_deduction(
        "2035-01-01"
    ) != baseline.gov.irs.deductions.standard.amount.SINGLE("2035-01-01")
    assert amt_bracket("2035-01-01") != baseline.gov.irs.income.amt.brackets[
        1
    ].threshold("2035-01-01")


def test_reform_does_not_change_social_security_benefit_tax_thresholds():
    baseline = _parameters()
    reformed = _parameters((create_trustees_core_thresholds_reform(),))

    baseline_threshold = (
        baseline.gov.irs.social_security.taxability.threshold.base.main.SINGLE
    )
    reformed_threshold = (
        reformed.gov.irs.social_security.taxability.threshold.base.main.SINGLE
    )

    for year in [2034, 2035, 2100]:
        instant = f"{year}-01-01"
        assert reformed_threshold(instant) == baseline_threshold(instant)
