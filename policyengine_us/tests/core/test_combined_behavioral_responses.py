"""Combined response measurements must work from a cold cache in either order."""

import numpy as np
import pytest
from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BEHAVIORAL_RESPONSE_CACHE_ATTR,
    BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
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
