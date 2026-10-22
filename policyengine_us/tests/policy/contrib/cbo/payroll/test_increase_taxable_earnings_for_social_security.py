"""Activation and invariants that fixed policy examples cannot exercise.

Only the activation test constructs a reformed model, once, for one person.
Hypothesis calls the actual variable formulas on small NumPy vectors with
read-only parameter stubs; it does not rebuild models or copy parameter trees.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings, strategies as st
from policyengine_core.parameters import Parameter
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.cbo.payroll.increase_taxable_earnings_for_social_security import (
    create_increase_taxable_earnings_for_social_security,
    create_increase_taxable_earnings_for_social_security_reform,
)
from policyengine_us.system import system
from policyengine_us.variables.gov.irs.tax.payroll.social_security.employee_social_security_tax import (
    employee_social_security_tax,
)
from policyengine_us.variables.gov.irs.tax.payroll.social_security.employer_social_security_tax import (
    employer_social_security_tax,
)
from policyengine_us.variables.gov.irs.tax.payroll.social_security.taxable_earnings_for_social_security import (
    taxable_earnings_for_social_security,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_social_security_tax import (
    self_employment_social_security_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.social_security_taxable_self_employment_income import (
    social_security_taxable_self_employment_income,
)

WAGE_BASE = "taxable_earnings_for_social_security"
SE_BASE = "social_security_taxable_self_employment_income"
TAXES = (
    "employee_social_security_tax",
    "employer_social_security_tax",
    "self_employment_social_security_tax",
)
BASELINE_VARIABLES = {
    variable.__name__: variable
    for variable in (
        taxable_earnings_for_social_security,
        social_security_taxable_self_employment_income,
        employee_social_security_tax,
        employer_social_security_tax,
        self_employment_social_security_tax,
    )
}


def test_future_threshold_activates_with_default_start_instant():
    reform = Reform.from_dict(
        {
            "gov.contrib.cbo.payroll.secondary_earnings_threshold": {
                "2026-01-01.2100-12-31": 250_000
            }
        },
        country_id="us",
    )
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "payroll_tax_gross_wages": {2025: 400_000, 2026: 400_000},
                    "taxable_self_employment_income": {2025: 50_000, 2026: 50_000},
                }
            }
        },
        reform=reform,
    )

    # The public parameter-only path must discover a 2026 start even though
    # Simulation's default start_instant is 2024-01-01. The wage base is the
    # current-law cap in 2025, then cap + ($400,000 - $250,000) in 2026.
    for year, extra_wages, expected_se in ((2025, 0, 0), (2026, 150_000, 50_000)):
        cap = system.parameters(f"{year}-01-01").gov.irs.payroll.social_security.cap
        assert simulation.calculate(WAGE_BASE, year)[0] == pytest.approx(
            cap + extra_wages
        )
        assert simulation.calculate(SE_BASE, year)[0] == pytest.approx(expected_se)


@pytest.mark.parametrize(
    ("future_threshold", "expected_active"),
    [(250_000, True), (np.inf, False)],
    ids=["distant-finite-interval", "always-infinite"],
)
def test_factory_detects_distant_finite_threshold(future_threshold, expected_active):
    threshold = Parameter(
        "gov.contrib.cbo.payroll.secondary_earnings_threshold",
        data={
            "2024-01-01": np.inf,
            "2036-01-01": future_threshold,
            "2037-01-01": np.inf,
        },
    )

    class Parameters(SimpleNamespace):
        def __call__(self, period):
            return _parameters(0, threshold(period))(period)

    parameters = Parameters(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                cbo=SimpleNamespace(
                    payroll=SimpleNamespace(secondary_earnings_threshold=threshold)
                )
            )
        )
    )
    # A finite interval twelve years away still requires the override, even
    # when the threshold is infinite both now and after that interval ends.
    reform = create_increase_taxable_earnings_for_social_security_reform(
        parameters, "2024-01-01"
    )
    assert (reform is not None) is expected_active


@pytest.fixture(scope="module")
def reform_variables():
    # Capture exactly the variable classes installed by Reform.apply without
    # constructing another full country model or mutating the shared system.
    overrides = []
    reform = create_increase_taxable_earnings_for_social_security()
    reform.apply(SimpleNamespace(update_variable=overrides.append))
    return BASELINE_VARIABLES | {variable.__name__: variable for variable in overrides}


def _parameters(cap, threshold):
    root = SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                payroll=SimpleNamespace(
                    social_security=SimpleNamespace(
                        cap=cap,
                        rate=SimpleNamespace(employee=0.062, employer=0.062),
                    )
                ),
                self_employment=SimpleNamespace(
                    rate=SimpleNamespace(social_security=0.124)
                ),
            ),
            contrib=SimpleNamespace(
                cbo=SimpleNamespace(
                    payroll=SimpleNamespace(secondary_earnings_threshold=threshold)
                )
            ),
        )
    )
    return lambda period: root


def _calculate(variables, wages, net_self_employment, parameters):
    values = {
        "payroll_tax_gross_wages": wages,
        "taxable_self_employment_income": net_self_employment,
    }

    def person(name, period):
        if name not in values:
            values[name] = variables[name].formula(person, period, parameters)
        return values[name]

    for variable in (WAGE_BASE, SE_BASE, *TAXES):
        person(variable, "2027")
    return values


CASE = st.tuples(
    st.integers(min_value=0, max_value=2_000_000),  # Gross payroll wages.
    st.integers(min_value=0, max_value=2_000_000),  # Net earnings subject to SECA.
    st.integers(min_value=0, max_value=1_000_000),  # Current-law wage cap.
    st.one_of(
        st.integers(min_value=0, max_value=1_000_000),
        st.just(np.inf),
    ),
)


@settings(max_examples=150, deadline=None, derandomize=True)
@given(cases=st.lists(CASE, min_size=1, max_size=12))
@example(
    cases=[
        (400_000, 0, 192_300, 250_000),
        (300_000, 46_175, 192_300, 250_000),
        (300_000, 100_000, 300_000, 250_000),
        (400_000, 50_000, 192_300, np.inf),
    ]
)
def test_donut_invariants(reform_variables, cases):
    wages, net_self_employment, cap, threshold = np.asarray(cases, dtype=float).T
    parameters = _parameters(cap, threshold)
    baseline = _calculate(BASELINE_VARIABLES, wages, net_self_employment, parameters)
    reformed = _calculate(reform_variables, wages, net_self_employment, parameters)

    baseline_tax = sum(baseline[variable] for variable in TAXES)
    reformed_tax = sum(reformed[variable] for variable in TAXES)
    assert np.all(reformed_tax >= baseline_tax - 1e-8)
    assert np.all(reformed[SE_BASE] >= 0)
    assert np.all(reformed["self_employment_social_security_tax"] >= 0)
    assert np.all(
        reformed[WAGE_BASE] + reformed[SE_BASE] <= wages + net_self_employment + 1e-8
    )

    # Combining the separately allocated wage and SE bases must recover the
    # full policy base: all earnings except the gap between cap and threshold.
    earnings = wages + net_self_employment
    expected_base = np.minimum(earnings, cap) + np.maximum(
        0, earnings - np.maximum(cap, threshold)
    )
    np.testing.assert_allclose(reformed[WAGE_BASE] + reformed[SE_BASE], expected_base)

    # Under current law taxable wages never exceed the cap, so adding the
    # zero floor preserves the old baseline SE base for every generated case.
    pre_clamp_se_base = np.minimum(net_self_employment, cap - baseline[WAGE_BASE])
    np.testing.assert_array_equal(baseline[SE_BASE], pre_clamp_se_base)

    # An infinite threshold must remain a no-op when the structural override
    # is active; this also protects the years before a future reform starts.
    inactive = np.isinf(threshold)
    for variable in (WAGE_BASE, SE_BASE, *TAXES):
        np.testing.assert_array_equal(
            reformed[variable][inactive], baseline[variable][inactive]
        )
