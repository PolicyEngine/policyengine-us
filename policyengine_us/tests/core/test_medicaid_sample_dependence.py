"""Reproduce Medicaid calibration failures with synthetic households.

Dataset-mode tests set the same flag as dataset loading, without loading
microdata. Python exercises population removal and reform branch selection,
which the policy YAML runner cannot express. Strict xfails retain the known
failures while valuation methodology awaits a choice.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.variables.gov.aca.slspc.slcsp_age_0 import (
    slcsp_age_0 as baseline_slcsp_age_0,
)


YEAR = 2026
AVERAGE = "medicaid_slcsp_state_average_cost_index"
DENOMINATOR = "medicaid_slcsp_state_denominator"
VALUE = "medicaid_cost_if_enrolled"


class DoublePremiums(Reform):
    def apply(self):
        class slcsp_age_0(baseline_slcsp_age_0):
            def formula(household, period, parameters):
                return 2 * baseline_slcsp_age_0.formula(household, period, parameters)

        self.update_variable(slcsp_age_0)


def _simulation(indices, weights, *, dataset=True, reform=None):
    names = [f"person_{i}" for i in range(len(indices))]
    situation = {
        "people": {
            name: {
                "age": {YEAR: 40},
                "person_weight": {YEAR: weight},
                "medicaid_enrolled": {YEAR: True},
                **(
                    {"medicaid_slcsp_cost_index": {YEAR: index}}
                    if index is not None
                    else {}
                ),
            }
            for name, index, weight in zip(names, indices, weights)
        },
        **{
            group: {name: {"members": [name]} for name in names}
            for group in ("tax_units", "spm_units", "families", "marital_units")
        },
        "households": {
            name: {
                "members": [name],
                "state_code": {YEAR: "TX"},
                "slcsp_rating_area": {f"{YEAR}-01": 1},
            }
            for name in names
        },
    }
    simulation = Simulation(situation=situation, reform=reform)
    simulation.is_over_dataset = dataset
    if simulation.baseline is not None:
        simulation.baseline.is_over_dataset = dataset
    return simulation


def _spending(simulation):
    return simulation.tax_benefit_system.parameters(
        f"{YEAR}-01-01"
    ).calibration.gov.hhs.medicaid.totals.spending.TX


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Dataset formulas recalculate state totals after households are removed",
)
def test_removing_an_unrelated_household_preserves_medicaid_value():
    full = _simulation([100, 100], [1_000, 1_000])
    subset = _simulation([100], [1_000])
    # Full denominator = 2 * 1,000 * 100 = 200,000; subset = 100,000.
    # Each household should retain S / 2,000 when its peer is removed.
    expected = full.calculate(VALUE, YEAR)[0]
    actual = subset.calculate(VALUE, YEAR)[0]
    assert actual == pytest.approx(expected)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Household formulas infer the state average from unrelated households",
)
def test_adding_an_unrelated_household_preserves_medicaid_value():
    alone = _simulation([100], [1], dataset=False)
    together = _simulation([100, 300], [1, 1], dataset=False)
    # The first person's index stays 100; adding a peer raises the inferred
    # state average from 100 to 200 and halves the first person's value.
    assert together.calculate(VALUE, YEAR)[0] == pytest.approx(
        alone.calculate(VALUE, YEAR)[0]
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Reform premiums use the unreformed allocation denominator",
)
def test_premium_reform_preserves_full_reference_state_spending():
    simulation = _simulation([None], [1_000], reform=DoublePremiums)
    baseline_index = simulation.baseline.calculate("medicaid_slcsp_cost_index", YEAR)
    reform_index = simulation.calculate("medicaid_slcsp_cost_index", YEAR)
    if not np.allclose(reform_index, 2 * baseline_index) or not np.all(
        baseline_index > 0
    ):
        raise ValueError("The reform must double positive premium indices")
    # With fixed enrollment, doubling every index should leave S unchanged:
    # 1,000 * S * (2 * index) / (1,000 * 2 * index) = S.
    # Reading the baseline denominator instead allocates 2 * S.
    total = np.dot([1_000], simulation.calculate(VALUE, YEAR))
    assert total == pytest.approx(_spending(simulation), rel=1e-6)


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    first_index=st.integers(1, 1_000),
    second_index=st.integers(1, 1_000),
    first_weight=st.integers(1, 10_000),
    second_weight=st.integers(1, 10_000),
)
def test_materialized_reference_totals_preserve_values_across_splits(
    first_index, second_index, first_weight, second_weight
):
    full = _simulation([first_index, second_index], [first_weight, second_weight])
    # Both enrollees have positive indices, so D = w1*i1 + w2*i2.
    denominator = first_weight * first_index + second_weight * second_index
    average = denominator / (first_weight + second_weight)
    expected = (
        _spending(full)
        * np.array([first_index, second_index], dtype=float)
        / denominator
    )
    np.testing.assert_allclose(full.calculate(AVERAGE, YEAR), average, rtol=1e-6)
    np.testing.assert_allclose(
        full.calculate(DENOMINATOR, YEAR), denominator, rtol=1e-6
    )
    original = full.calculate(VALUE, YEAR)
    np.testing.assert_allclose(original, expected, rtol=1e-6)
    for index, weight, value in zip(
        [first_index, second_index], [first_weight, second_weight], original
    ):
        subset = _simulation([index], [weight])
        subset.set_input(AVERAGE, YEAR, [average])
        subset.set_input(DENOMINATOR, YEAR, [denominator])
        np.testing.assert_allclose(subset.calculate(VALUE, YEAR), [value], rtol=1e-6)
    assert np.dot([first_weight, second_weight], original) == pytest.approx(
        _spending(full), rel=1e-6
    )
