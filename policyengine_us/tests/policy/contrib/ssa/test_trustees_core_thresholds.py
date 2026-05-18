import math
from functools import lru_cache

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.reforms.ssa.trustees_core_thresholds import (
    TRUSTEES_CORE_THRESHOLD_ASSUMPTION,
    create_trustees_core_thresholds_reform,
)


@lru_cache
def _parameters(reform=None):
    return CountryTaxBenefitSystem(reform=reform).parameters


@lru_cache
def _trustees_parameters():
    return _parameters((create_trustees_core_thresholds_reform(),))


def test_metadata_marks_trustees_core_thresholds_as_explicit_assumption():
    assert (
        TRUSTEES_CORE_THRESHOLD_ASSUMPTION["name"] == "trustees-2025-core-thresholds-v1"
    )
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["not_default_current_law"] is True
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["start_year"] == 2035
    assert "economic_assumption" not in TRUSTEES_CORE_THRESHOLD_ASSUMPTION
    assert "income_uprating_assumption" not in TRUSTEES_CORE_THRESHOLD_ASSUMPTION
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["wage_index"] == "gov.ssa.nawi"
    assert (
        "all_gov_irs_uprating_parameters"
        in TRUSTEES_CORE_THRESHOLD_ASSUMPTION["parameter_groups"]
    )
    assert (
        TRUSTEES_CORE_THRESHOLD_ASSUMPTION["uprating_parameter"] == "gov.irs.uprating"
    )
    assert "OACT email clarification" in TRUSTEES_CORE_THRESHOLD_ASSUMPTION["source"]


def test_reform_leaves_long_run_economic_assumptions_unchanged():
    baseline = _parameters()
    reformed = _trustees_parameters()

    assert reformed.gov.ssa.nawi("2100-01-01") == baseline.gov.ssa.nawi("2100-01-01")
    assert reformed.gov.irs.payroll.social_security.cap(
        "2100-01-01"
    ) == baseline.gov.irs.payroll.social_security.cap("2100-01-01")

    for parameter_name in [
        "employment_income",
        "social_security",
        "taxable_pension_income",
    ]:
        baseline_parameter = getattr(baseline.calibration.gov.irs.soi, parameter_name)
        reformed_parameter = getattr(reformed.calibration.gov.irs.soi, parameter_name)
        assert reformed_parameter("2100-01-01") == baseline_parameter("2100-01-01")


def test_reform_only_changes_federal_irs_uprating_parameters():
    baseline = _parameters()
    reformed = _trustees_parameters()
    reformed_parameters_by_name = {
        parameter.name: parameter
        for parameter in [reformed, *reformed.get_descendants()]
        if parameter.__class__.__name__ == "Parameter"
    }
    changed_names = []

    for parameter in [baseline, *baseline.get_descendants()]:
        if parameter.__class__.__name__ != "Parameter":
            continue

        reformed_parameter = reformed_parameters_by_name[parameter.name]

        if parameter("2100-01-01") == reformed_parameter("2100-01-01"):
            continue

        uprating = parameter.metadata.get("uprating")
        uprating_parameter = (
            uprating.get("parameter") if isinstance(uprating, dict) else uprating
        )
        assert parameter.name.startswith("gov.irs.")
        assert uprating_parameter == "gov.irs.uprating"
        changed_names.append(parameter.name)

    assert changed_names


def test_social_security_components_use_aggregate_ss_uprater():
    from policyengine_us.variables.gov.ssa.ss.social_security_dependents import (
        social_security_dependents,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_disability import (
        social_security_disability,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_retirement import (
        social_security_retirement,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_survivors import (
        social_security_survivors,
    )

    expected_uprater = "calibration.gov.irs.soi.social_security"
    assert social_security_retirement.uprating == expected_uprater
    assert social_security_disability.uprating == expected_uprater
    assert social_security_dependents.uprating == expected_uprater
    assert social_security_survivors.uprating == expected_uprater


def test_reform_wage_indexes_core_tax_threshold_from_2035():
    baseline = _parameters()
    reformed = _trustees_parameters()

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
    reformed = _trustees_parameters()

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


def test_reform_wage_indexes_indexed_credit_parameters():
    baseline = _parameters()
    reformed = _trustees_parameters()
    nawi = reformed.gov.ssa.nawi

    eitc_max = reformed.gov.irs.credits.eitc.max.brackets[3].amount
    baseline_eitc_max = baseline.gov.irs.credits.eitc.max.brackets[3].amount

    assert eitc_max("2034-01-01") == baseline_eitc_max("2034-01-01")
    nawi_growth = float(nawi("2034-01-01")) / float(nawi("2033-01-01"))
    expected_eitc_2035 = math.floor(float(eitc_max("2034-01-01")) * nawi_growth + 0.5)
    assert eitc_max("2035-01-01") == expected_eitc_2035
    assert eitc_max("2035-01-01") != baseline_eitc_max("2035-01-01")

    ctc_base = reformed.gov.irs.credits.ctc.amount.base.brackets[0].amount
    baseline_ctc_base = baseline.gov.irs.credits.ctc.amount.base.brackets[0].amount
    ctc_ratio_2040 = float(nawi("2039-01-01")) / float(nawi("2033-01-01"))
    expected_ctc_2040 = (
        math.floor(float(ctc_base("2034-01-01")) * ctc_ratio_2040 / 100) * 100
    )

    assert ctc_base("2034-01-01") == baseline_ctc_base("2034-01-01")
    assert ctc_base("2040-01-01") == expected_ctc_2040
    assert ctc_base("2040-01-01") != baseline_ctc_base("2040-01-01")

    ctc_refundable_max = reformed.gov.irs.credits.ctc.refundable.individual_max
    baseline_ctc_refundable_max = baseline.gov.irs.credits.ctc.refundable.individual_max
    ctc_refundable_ratio_2040 = float(nawi("2039-01-01")) / float(nawi("2033-01-01"))
    expected_ctc_refundable_2040 = (
        math.floor(
            float(ctc_refundable_max("2034-01-01")) * ctc_refundable_ratio_2040 / 100
        )
        * 100
    )

    assert ctc_refundable_max("2034-01-01") == baseline_ctc_refundable_max("2034-01-01")
    assert ctc_refundable_max("2040-01-01") == expected_ctc_refundable_2040
    assert ctc_refundable_max("2040-01-01") != baseline_ctc_refundable_max("2040-01-01")


def test_reform_does_not_change_social_security_benefit_tax_thresholds():
    baseline = _parameters()
    reformed = _trustees_parameters()

    baseline_threshold = (
        baseline.gov.irs.social_security.taxability.threshold.base.main.SINGLE
    )
    reformed_threshold = (
        reformed.gov.irs.social_security.taxability.threshold.base.main.SINGLE
    )

    for year in [2034, 2035, 2100]:
        instant = f"{year}-01-01"
        assert reformed_threshold(instant) == baseline_threshold(instant)


def test_reform_does_not_change_state_parameters_using_irs_uprating():
    baseline = _parameters()
    reformed = _trustees_parameters()

    baseline_state_ctc = baseline.gov.states.dc.tax.income.credits.ctc.amount
    reformed_state_ctc = reformed.gov.states.dc.tax.income.credits.ctc.amount

    uprating = baseline_state_ctc.metadata["uprating"]
    uprating_parameter = (
        uprating["parameter"] if isinstance(uprating, dict) else uprating
    )
    assert uprating_parameter == "gov.irs.uprating"

    for year in [2034, 2035, 2040, 2100]:
        instant = f"{year}-01-01"
        assert reformed_state_ctc(instant) == baseline_state_ctc(instant)
