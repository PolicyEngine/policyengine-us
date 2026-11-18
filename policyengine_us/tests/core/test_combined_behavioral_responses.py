"""Combined response measurements must work from a cold cache in either order."""

import numpy as np
import pytest
from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform

import policyengine_us.variables.household.marginal_tax_rate_helpers as marginal_rate_helpers
from policyengine_us import Simulation
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BEHAVIORAL_RESPONSE_CACHE_ATTR,
    BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    get_behavioral_response_measurements,
)

YEAR = 2026
RESPONSES = (
    "capital_gains_behavioral_response",
    "labor_supply_behavioral_response",
)


def combined_simulation(fixed_net_income=False):
    date_range = "2020-01-01.2100-12-31"
    policy = Reform.from_dict(
        {
            "gov.irs.income.bracket.rates.3": {date_range: 0.32},
            "gov.irs.capital_gains.rates.2": {date_range: 0.20},
            "gov.simulation.labor_supply_responses.elasticities.income": {
                date_range: -0.05
            },
            "gov.simulation.labor_supply_responses.elasticities.substitution.all": {
                date_range: 0.25
            },
            "gov.simulation.capital_gains_responses.elasticity": {date_range: -0.62},
        },
        country_id="us",
    )
    situation = {
        "people": {
            "worker": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 60_000},
                "long_term_capital_gains": {YEAR: 15_000},
                "weekly_hours_worked": {YEAR: 40},
            }
        },
        **{
            entity: {"unit": {"members": ["worker"]}}
            for entity in ("tax_units", "spm_units", "families", "marital_units")
        },
        "households": {
            "household": {
                "members": ["worker"],
                "state_code": {YEAR: "TX"},
            }
        },
    }
    if fixed_net_income:
        situation["households"]["household"]["household_net_income"] = {YEAR: 60_000}
    return Simulation(situation=situation, reform=policy)


def test_combined_measurements_keep_inputs_set_on_baseline_and_reform(monkeypatch):
    """Measurement branches and their raised branches retain identification.

    Fixed net income skips benefit calculations while real measurement and
    rate branches expose the input-preservation invariant. Independent Texas
    federal and health MTR tests cover the actual CTC policy consequences.
    The one-person setup and fixed income limit additional CI cost.
    """
    identification = np.array([False])
    simulation = combined_simulation(fixed_net_income=True)
    for current in (simulation, simulation.baseline):
        current.set_input("has_itin", YEAR, identification)
    caller_arrays = [
        (
            current,
            {
                variable: current.get_array(variable, YEAR).copy()
                for variable in (
                    "has_itin",
                    "employment_income_before_lsr",
                    "long_term_capital_gains_before_response",
                    "weekly_hours_worked_before_lsr",
                    "household_net_income",
                )
            },
        )
        for current in (simulation, simulation.baseline)
    ]
    observed = {}
    create_branch = marginal_rate_helpers.create_perturbed_branch

    def observe_raised_branch(parent, period, branch_name, increments):
        branch = create_branch(parent, period, branch_name, increments)
        assert branch.parent_branch is parent
        assert branch.branch_name == branch_name
        np.testing.assert_array_equal(
            parent.get_array("has_itin", YEAR), identification
        )
        kind = (
            "capital_gains" if "long_term_capital_gains" in increments else "earnings"
        )
        value = branch.get_array("has_itin", YEAR)
        observed.setdefault((parent.branch_name, kind), []).append(
            None if value is None else value.copy()
        )
        return branch

    # Earnings imports the helper module; Core dynamically loads the capital
    # gains formula, whose helper binding lives in its actual globals.
    monkeypatch.setattr(
        marginal_rate_helpers, "create_perturbed_branch", observe_raised_branch
    )
    for current in (simulation, simulation.baseline):
        formula = current.tax_benefit_system.variables[
            "marginal_tax_rate_on_capital_gains"
        ].get_formula(make_period(YEAR))
        monkeypatch.setitem(
            formula.__globals__, "create_perturbed_branch", observe_raised_branch
        )
    measurements = get_behavioral_response_measurements(
        simulation.person, make_period(YEAR)
    )
    expected_paths = {
        (parent, kind)
        for parent in (
            BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
            BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
        )
        for kind in ("earnings", "capital_gains")
    }
    assert set(observed) == expected_paths
    for path, arrays in observed.items():
        for value in arrays:
            np.testing.assert_array_equal(value, identification, err_msg=str(path))
    for name in ("baseline", "reform"):
        np.testing.assert_array_equal(measurements[f"{name}_net_income"], [60_000])
        np.testing.assert_array_equal(measurements[f"{name}_mtr"], [1])
        np.testing.assert_array_equal(measurements[f"{name}_capital_gains_mtr"], [1])
    for current, arrays in caller_arrays:
        for variable, value in arrays.items():
            np.testing.assert_array_equal(current.get_array(variable, YEAR), value)
        assert BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH not in current.branches
        assert BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH not in current.branches


@pytest.mark.parametrize(
    "query_order",
    [RESPONSES, RESPONSES[::-1]],
    ids=["capital-gains-first", "labor-supply-first"],
)
def test_combined_responses_measure_from_a_cold_cache_in_either_order(query_order):
    """CG-first measurement must not recursively calculate the hours response.

    Supplying household net income bypasses program calculations involving
    hours, isolating the eager hours calculation in the marginal-rate helper.
    The fixed income also makes both responses zero despite nonzero
    elasticities: neither the measured income nor the measured marginal rates
    change under the reform.
    """
    simulation = combined_simulation(fixed_net_income=True)
    period_key = str(make_period(YEAR))
    assert period_key not in getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR, {})

    for response in query_order:
        np.testing.assert_array_equal(simulation.calculate(response, YEAR), [0])

    np.testing.assert_array_equal(
        simulation.calculate("weekly_hours_worked_behavioural_response", YEAR), [0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("weekly_hours_worked", YEAR), [40]
    )
    assert period_key in getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR)
    assert BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH not in simulation.branches
    assert (
        BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH
        not in simulation.baseline.branches
    )


def test_nonzero_combined_responses_are_independent_of_query_order():
    """Shared measurements give the same income and hours changes in both orders."""
    results = []
    measurements = []
    period_key = str(make_period(YEAR))
    for query_order in (RESPONSES, RESPONSES[::-1]):
        simulation = combined_simulation()
        assert period_key not in getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR, {})
        response_values = {
            variable: simulation.calculate(variable, YEAR) for variable in query_order
        }
        response_values["weekly_hours_worked_behavioural_response"] = (
            simulation.calculate("weekly_hours_worked_behavioural_response", YEAR)
        )
        assert response_values["capital_gains_behavioral_response"][0] == pytest.approx(
            -2_450.4, abs=0.5
        )
        assert abs(response_values["labor_supply_behavioral_response"][0]) > 1
        assert abs(response_values["weekly_hours_worked_behavioural_response"][0]) > 0
        results.append(response_values)
        measurements.append(
            getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR)[period_key]
        )

    for variable in results[0]:
        np.testing.assert_allclose(
            results[0][variable], results[1][variable], atol=1e-3, err_msg=variable
        )
    for measurement in measurements[0]:
        np.testing.assert_allclose(
            measurements[0][measurement],
            measurements[1][measurement],
            atol=1e-3,
            err_msg=measurement,
        )
