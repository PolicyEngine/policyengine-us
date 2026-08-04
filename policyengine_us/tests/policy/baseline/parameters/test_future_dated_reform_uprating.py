"""Parametric reforms must not disturb parameter values before their start date.

Regression tests for https://github.com/PolicyEngine/policyengine-us/issues/9075:
applying the reform set before ``uprate_parameters`` made a reform value at a
future date act as the parameter's last defined value, so the years between the
last legislated value and the reform start silently lost their uprating and
reverted to the last legislated nominal value.
"""

from policyengine_core.reforms import Reform

from policyengine_us.system import CountryTaxBenefitSystem, system

# An uprated parameter (gov.irs.uprating, $0.01 rounding) with its last
# legislated value in 2025, so 2026+ baseline values exist only via uprating.
REFORMED_PARAMETER = "gov.states.or.tax.income.credits.ctc.reduction.start"
REFORM_VALUE = 40_000

BASELINE = system.parameters.get_child(REFORMED_PARAMETER)


def build_reformed_parameter(period_key):
    reform = Reform.from_dict(
        {REFORMED_PARAMETER: {period_key: REFORM_VALUE}},
        country_id="us",
    )
    reformed_system = CountryTaxBenefitSystem(reform=(reform,))
    return reformed_system.parameters.get_child(REFORMED_PARAMETER)


def test_baseline_parameter_uprates():
    # Guard: the assertions below only discriminate if the baseline actually
    # uprates this parameter past its last legislated value.
    assert BASELINE("2026-01-01") > BASELINE("2025-01-01")
    assert BASELINE("2028-01-01") > BASELINE("2026-01-01")


def test_future_dated_range_reform_preserves_uprating_before_start():
    reformed = build_reformed_parameter("2029-01-01.2100-12-31")
    for year in (2025, 2026, 2027, 2028):
        assert reformed(f"{year}-01-01") == BASELINE(f"{year}-01-01")
    # Within the window, the reform value applies as given (no uprating).
    for year in (2029, 2035, 2100):
        assert reformed(f"{year}-01-01") == REFORM_VALUE


def test_future_dated_from_onward_reform_preserves_uprating_before_start():
    reformed = build_reformed_parameter("2029-01-01")
    for year in (2025, 2026, 2027, 2028):
        assert reformed(f"{year}-01-01") == BASELINE(f"{year}-01-01")
    # A bare-instant key applies from that instant onward, flattening any
    # later scheduled breakpoints such as uprating.
    for year in (2029, 2035, 2100):
        assert reformed(f"{year}-01-01") == REFORM_VALUE


def test_current_law_period_reform_unchanged_before_start():
    reformed = build_reformed_parameter("2024-01-01.2100-12-31")
    assert reformed("2023-01-01") == BASELINE("2023-01-01")
    for year in (2024, 2026, 2100):
        assert reformed(f"{year}-01-01") == REFORM_VALUE


def test_reformed_parameter_keeps_modified_flag():
    # The macro-impact cache treats ``modified`` as "this parameter differs
    # from current law", so the reformed parameter must keep the flag and an
    # untouched parameter must not gain it.
    reform = Reform.from_dict(
        {REFORMED_PARAMETER: {"2029-01-01.2100-12-31": REFORM_VALUE}},
        country_id="us",
    )
    reformed_system = CountryTaxBenefitSystem(reform=(reform,))
    assert reformed_system.parameters.get_child(REFORMED_PARAMETER).modified
    untouched = reformed_system.parameters.get_child(
        "gov.irs.deductions.standard.amount.SINGLE"
    )
    assert not untouched.modified
