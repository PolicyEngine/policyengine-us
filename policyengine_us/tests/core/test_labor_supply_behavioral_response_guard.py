from types import SimpleNamespace
from unittest.mock import Mock, patch

from policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response import (
    labor_supply_behavioral_response,
)


def _parameters(*, income=0, substitution_all=0, substitution_secondary=0, primary_1=0):
    return lambda period: SimpleNamespace(
        gov=SimpleNamespace(
            simulation=SimpleNamespace(
                labor_supply_responses=SimpleNamespace(
                    elasticities=SimpleNamespace(
                        income=income,
                        substitution=SimpleNamespace(
                            all=substitution_all,
                            by_position_and_decile=SimpleNamespace(
                                secondary=substitution_secondary,
                                primary=SimpleNamespace(
                                    **{
                                        str(decile): primary_1 if decile == 1 else 0
                                        for decile in range(1, 11)
                                    }
                                ),
                            ),
                        ),
                    )
                )
            )
        )
    )


def _person():
    person = Mock()
    person.simulation = Mock()
    person.simulation.baseline = Mock()
    person.simulation._lsr_calculating = False
    return person


def test_guard_returns_zero_only_when_all_elasticities_are_zero():
    result = labor_supply_behavioral_response.formula(_person(), 2026, _parameters())

    assert result == 0


@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_substitution_lsr_effect",
    return_value=500,
)
@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_income_lsr_effect",
    return_value=0,
)
@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.get_behavioral_response_measurements",
    return_value={"baseline_net_income": 1},
)
def test_guard_does_not_short_circuit_primary_decile_responses(
    mock_measurements,
    mock_income,
    mock_substitution,
):
    result = labor_supply_behavioral_response.formula(
        _person(), 2026, _parameters(primary_1=0.2)
    )

    assert result == 500
    mock_measurements.assert_called_once()
    mock_income.assert_called_once()
    mock_substitution.assert_called_once()


@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_substitution_lsr_effect",
    return_value=250,
)
@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_income_lsr_effect",
    return_value=0,
)
@patch(
    "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.get_behavioral_response_measurements",
    return_value={"baseline_net_income": 1},
)
def test_guard_does_not_short_circuit_secondary_responses(
    mock_measurements,
    mock_income,
    mock_substitution,
):
    result = labor_supply_behavioral_response.formula(
        _person(), 2026, _parameters(substitution_secondary=0.15)
    )

    assert result == 250
    mock_measurements.assert_called_once()
    mock_income.assert_called_once()
    mock_substitution.assert_called_once()
