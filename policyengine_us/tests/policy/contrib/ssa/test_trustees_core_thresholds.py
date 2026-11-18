import math
from functools import lru_cache

from policyengine_core.parameters import Parameter

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.reforms.ssa import trustees_core_threshold_parameters
from policyengine_us.reforms.ssa.trustees_core_thresholds import (
    TRUSTEES_CORE_THRESHOLD_ASSUMPTION,
    create_trustees_core_thresholds_reform,
)

STANDARD = "gov.irs.deductions.standard.amount"
STANDARD_DEDUCTIONS = tuple(
    f"{STANDARD}.{status}"
    for status in (
        "SINGLE",
        "JOINT",
        "SEPARATE",
        "HEAD_OF_HOUSEHOLD",
        "SURVIVING_SPOUSE",
    )
)
# IRS indices the reform leaves on prices. 213(d)(10)(B) indexes the
# long-term care premium limits by medical care prices; before this index
# existed they uprated by gov.bls.cpi.cpi_u_medical_care, outside the
# reform's selection, and they stay off the wage path.
EXCLUDED_IRS_INDICES = {"gov.irs.indexing.medical_care_c_cpi_u"}


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
    assert TRUSTEES_CORE_THRESHOLD_ASSUMPTION["uprating_parameters"] == (
        "gov.irs.uprating",
        "gov.irs.indexing.c_cpi_u",
        "gov.irs.indexing.hsa_c_cpi_u",
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
    """The reform moves IRS parameters on the CPI indices it names, and
    parameters that uprate by one of those, such as the joint standard
    deduction, which follows the single amount."""
    baseline = _parameters()
    reformed = _trustees_parameters()
    reformed_parameters_by_name = {
        parameter.name: parameter
        for parameter in [reformed, *reformed.get_descendants()]
        if parameter.__class__.__name__ == "Parameter"
    }
    uprating_by_name = {}

    for parameter in [baseline, *baseline.get_descendants()]:
        if parameter.__class__.__name__ != "Parameter":
            continue

        reformed_parameter = reformed_parameters_by_name[parameter.name]

        if parameter("2100-01-01") == reformed_parameter("2100-01-01"):
            continue

        uprating = parameter.metadata.get("uprating")
        assert parameter.name.startswith("gov.irs.")
        uprating_by_name[parameter.name] = (
            uprating.get("parameter") if isinstance(uprating, dict) else uprating
        )

    indices = TRUSTEES_CORE_THRESHOLD_ASSUMPTION["uprating_parameters"]
    for name, uprating_parameter in uprating_by_name.items():
        assert (
            uprating_parameter in indices or uprating_parameter in uprating_by_name
        ), name
    assert set(uprating_by_name.values()) >= set(indices)
    standard = "gov.irs.deductions.standard.amount"
    for status in ("JOINT", "SURVIVING_SPOUSE"):
        assert uprating_by_name[f"{standard}.{status}"] == f"{standard}.SINGLE"


def test_joint_standard_deduction_stays_twice_the_single_amount():
    """26 U.S.C. 63(c)(2)(A): 200% of the single amount, on the wage path too."""
    standard = _trustees_parameters().gov.irs.deductions.standard.amount
    baseline = _parameters().gov.irs.deductions.standard.amount
    for year in range(2026, 2101):
        period = f"{year}-01-01"
        assert standard.JOINT(period) == 2 * standard.SINGLE(period), year
        assert standard.SURVIVING_SPOUSE(period) == standard.JOINT(period), year
        assert standard.SEPARATE(period) == standard.SINGLE(period), year
    assert standard.SINGLE("2100-01-01") != baseline.SINGLE("2100-01-01")


def test_reported_social_security_components_use_aggregate_ss_uprater():
    from policyengine_us.variables.gov.ssa.ss.social_security_dependents import (
        social_security_dependents,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_dependents_reported import (
        social_security_dependents_reported,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_disability import (
        social_security_disability,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_disability_reported import (
        social_security_disability_reported,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_retirement import (
        social_security_retirement,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_retirement_reported import (
        social_security_retirement_reported,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_survivors import (
        social_security_survivors,
    )
    from policyengine_us.variables.gov.ssa.ss.social_security_survivors_reported import (
        social_security_survivors_reported,
    )

    expected_uprater = "calibration.gov.irs.soi.social_security"
    for public, reported in (
        (social_security_retirement, social_security_retirement_reported),
        (social_security_disability, social_security_disability_reported),
        (social_security_dependents, social_security_dependents_reported),
        (social_security_survivors, social_security_survivors_reported),
    ):
        assert reported.uprating == expected_uprater
        assert "uprating" not in public.__dict__


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


def test_head_of_household_stays_its_base_plus_whole_50_dollar_steps():
    """26 U.S.C. 63(c)(7)(B)(ii) rounds the increase over $23,625 down to a
    multiple of $50, so on the wage path too the head of household amount
    is $23,625 plus whole $50 steps. The single amount's base, $15,750, is a
    multiple of $50, so rounding its increase gives the values that
    rounding its total gave before."""
    reformed = _trustees_parameters()
    standard = reformed.gov.irs.deductions.standard.amount
    nawi = reformed.gov.ssa.nawi
    base_nawi = float(nawi("2033-01-01"))
    head_2034 = float(standard.HEAD_OF_HOUSEHOLD("2034-01-01"))
    single_2034 = float(standard.SINGLE("2034-01-01"))
    for year in range(2035, 2101):
        ratio = float(nawi(f"{year - 1}-01-01")) / base_nawi
        head = standard.HEAD_OF_HOUSEHOLD(f"{year}-01-01")
        assert (head - 23_625) % 50 == 0, year
        assert head == 23_625 + math.floor((head_2034 * ratio - 23_625) / 50) * 50
        # The arithmetic before increases were rounded: the total, down to $50.
        single = standard.SINGLE(f"{year}-01-01")
        assert single == math.floor(single_2034 * ratio / 50) * 50, year


def test_core_threshold_parameters_list_what_the_reform_changes():
    """The public list crfb-tob-impacts and others can read: every parameter
    the reform re-projects, leaders before followers, once each."""
    baseline = _parameters()
    reformed = _trustees_parameters()
    listed = trustees_core_threshold_parameters(baseline)
    names = [parameter.name for parameter in listed]
    assert len(names) == len(set(names))
    assert names == [p.name for p in trustees_core_threshold_parameters(baseline)]
    assert set(STANDARD_DEDUCTIONS) <= set(names)
    for follower in ("JOINT", "SURVIVING_SPOUSE"):
        assert names.index(f"{STANDARD}.SINGLE") < names.index(f"{STANDARD}.{follower}")

    reformed_by_name = {
        parameter.name: parameter
        for parameter in reformed.get_descendants()
        if isinstance(parameter, Parameter)
    }
    changed = set()
    for parameter in baseline.get_descendants():
        if not isinstance(parameter, Parameter):
            continue
        reformed_parameter = reformed_by_name[parameter.name]
        for year in (2035, 2036, 2040, 2050, 2075, 2100):
            if parameter(f"{year}-01-01") != reformed_parameter(f"{year}-01-01"):
                changed.add(parameter.name)
                break
    assert changed <= set(names), changed - set(names)
    assert set(STANDARD_DEDUCTIONS) <= changed


def test_every_irs_index_is_wage_indexed_or_excluded():
    """A parameter moved to a new IRS index leaves the Trustees set unless
    the index joins the assumption's tuple or this exclusion list."""
    indexing = _parameters().gov.irs.indexing
    indices = {child.name for child in indexing.children.values()}
    selected = set(TRUSTEES_CORE_THRESHOLD_ASSUMPTION["uprating_parameters"])
    assert not selected & EXCLUDED_IRS_INDICES
    assert indices == (selected - {"gov.irs.uprating"}) | EXCLUDED_IRS_INDICES
