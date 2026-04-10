"""Unit tests for labor_supply_behavioral_response with 100% coverage."""

import pytest
from unittest.mock import Mock, patch
from policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response import (
    labor_supply_behavioral_response,
)


def _mock_parameters(
    *,
    income_all=0,
    income_base=0,
    substitution_all=0,
    primary_decile_1=0,
    secondary=0,
):
    parameters = Mock()
    p = Mock()
    income = Mock()
    income.all = income_all
    income.base = income_base
    substitution = Mock()
    substitution.all = substitution_all
    primary = Mock()
    for decile in range(1, 11):
        setattr(primary, str(decile), primary_decile_1 if decile == 1 else 0)
    by_position = Mock()
    by_position.primary = primary
    by_position.secondary = secondary
    substitution.by_position_and_decile = by_position
    p.elasticities.income = income
    p.elasticities.substitution = substitution
    parameters.return_value.gov.simulation.labor_supply_responses = p
    return parameters


class TestLaborSupplyBehavioralResponse:
    """Test all code paths in labor_supply_behavioral_response."""

    # TEST 1: Lines 14-15 - No baseline returns 0
    def test_no_baseline_returns_zero(self):
        """Test that without baseline, returns 0 (lines 14-15)."""
        person = Mock()
        person.simulation.baseline = None
        period = Mock()
        parameters = _mock_parameters()

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )
        assert result == 0

    # TEST 2: Lines 16-17 - Zero elasticities returns 0
    def test_zero_elasticities_returns_zero(self):
        """Test that zero elasticities returns 0 (lines 16-17)."""
        person = Mock()
        person.simulation.baseline = Mock()  # Has baseline
        period = Mock()
        parameters = _mock_parameters()

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )
        assert result == 0

    # TEST 3: Lines 20-24 - Re-entry guard returns 0
    def test_reentry_guard_returns_zero(self):
        """Test re-entry guard prevents recursion (lines 20-24)."""
        person = Mock()
        simulation = Mock()
        simulation.baseline = Mock()
        simulation._lsr_calculating = True  # Already calculating
        person.simulation = simulation
        period = Mock()
        parameters = _mock_parameters(income_base=0.1, substitution_all=0.2)

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )
        assert result == 0

    # TEST 4: Non-zero elasticities use measured income and wage changes
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_substitution_lsr_effect"
    )
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_income_lsr_effect"
    )
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.get_behavioral_response_measurements"
    )
    def test_full_execution_path(
        self,
        mock_measurements,
        mock_income_effect,
        mock_substitution_effect,
    ):
        """Test complete execution with cached behavioral measurements."""
        person = Mock()
        simulation = Mock()
        simulation.baseline = Mock()
        simulation._lsr_calculating = False
        person.simulation = simulation
        period = Mock()
        parameters = _mock_parameters(income_base=0.1, substitution_all=0.2)
        measurements = {"reform_net_income": 1}
        mock_measurements.return_value = measurements
        mock_income_effect.return_value = 1_000
        mock_substitution_effect.return_value = 500

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )

        assert result == 1500.0
        assert simulation._lsr_calculating == False
        mock_measurements.assert_called_once_with(person, period)
        mock_income_effect.assert_called_once_with(
            person, period, parameters, measurements
        )
        mock_substitution_effect.assert_called_once_with(
            person, period, parameters, measurements
        )

    # TEST 5: Exceptions still clear the re-entry guard
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.get_behavioral_response_measurements"
    )
    def test_exception_handling_finally_block(self, mock_measurements):
        """Test exception handling ensures the re-entry guard resets."""
        person = Mock()
        simulation = Mock()
        simulation.baseline = Mock()
        simulation._lsr_calculating = False
        person.simulation = simulation
        period = Mock()
        parameters = _mock_parameters(income_base=0.1, substitution_all=0.2)
        mock_measurements.side_effect = ValueError("Test exception")

        with pytest.raises(ValueError):
            labor_supply_behavioral_response.formula(
                person, period, parameters
            )

        assert simulation._lsr_calculating == False

    # TEST 6: Measurements are shared between income and substitution effects
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_substitution_lsr_effect"
    )
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.calculate_income_lsr_effect"
    )
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.get_behavioral_response_measurements"
    )
    def test_measurements_shared_between_effects(
        self,
        mock_measurements,
        mock_income_effect,
        mock_substitution_effect,
    ):
        """Test that both effect calculators receive the same measurements."""
        person = Mock()
        simulation = Mock()
        simulation.baseline = Mock()
        simulation._lsr_calculating = False
        person.simulation = simulation
        period = Mock()
        parameters = _mock_parameters(income_base=0.1, substitution_all=0.2)
        measurements = {"baseline_net_income": 1}
        mock_measurements.return_value = measurements
        mock_income_effect.return_value = 700
        mock_substitution_effect.return_value = 300

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )

        assert result == 1000
        assert mock_income_effect.call_args.args[3] is measurements
        assert mock_substitution_effect.call_args.args[3] is measurements
