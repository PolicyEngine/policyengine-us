"""Unit tests for labor_supply_behavioral_response with 100% coverage."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response import (
    labor_supply_behavioral_response,
)


class TestLaborSupplyBehavioralResponse:
    """Test all code paths in labor_supply_behavioral_response."""

    # TEST 1: Lines 14-15 - No baseline returns 0
    def test_no_baseline_returns_zero(self):
        """Test that without baseline, returns 0 (lines 14-15)."""
        person = Mock()
        person.simulation.baseline = None
        period = Mock()
        parameters = Mock()

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
        parameters = Mock()

        # Set elasticities to 0
        p = Mock()
        p.elasticities.income = 0
        p.elasticities.substitution.all = 0
        parameters.return_value.gov.simulation.labor_supply_responses = p

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
        parameters = Mock()

        # Set non-zero elasticities
        p = Mock()
        p.elasticities.income = 0.1
        p.elasticities.substitution.all = 0.2
        parameters.return_value.gov.simulation.labor_supply_responses = p

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )
        assert result == 0

    # TEST 4: Lines 27-79 - Full execution path with mocked add()
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.add"
    )
    def test_full_execution_path(self, mock_add):
        """Test complete execution including branches (lines 27-79)."""
        # Setup
        mock_add.return_value = 1500.0

        person = Mock()
        simulation = Mock()
        baseline = Mock()
        baseline_mock = Mock()
        simulation.baseline = baseline

        # Setup the nested branches structure correctly
        baseline_branches = {"baseline_lsr_measurement": Mock()}
        baseline_mock.branches = baseline_branches
        simulation.branches = {
            "baseline": baseline_mock,
            "lsr_measurement": Mock(),
        }
        simulation._lsr_calculating = False

        # Mock branch creation
        measurement_branch = Mock()
        baseline_branch = Mock()
        baseline_branch.tax_benefit_system.parameters.simulation = Mock()

        # Setup get_branch to return correct branches
        def get_branch_side_effect(name, **kwargs):
            if name == "lsr_measurement":
                return measurement_branch
            elif name == "baseline":
                return baseline_mock

        simulation.get_branch.side_effect = get_branch_side_effect
        baseline_mock.get_branch.return_value = baseline_branch

        person.simulation = simulation
        person.return_value = (
            50000  # For employment/self-employment income calls
        )

        period = Mock()
        parameters = Mock()

        # Set non-zero elasticities
        p = Mock()
        p.elasticities.income = 0.1
        p.elasticities.substitution.all = 0.2
        parameters.return_value.gov.simulation.labor_supply_responses = p

        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )

        # Verify execution
        assert result == 1500.0
        assert simulation._lsr_calculating == False  # Finally block executed

        # Verify branches created (lines 30-35)
        simulation.get_branch.assert_any_call(
            "lsr_measurement", clone_system=True
        )

        # Verify neutralization (lines 44-50)
        measurement_branch.tax_benefit_system.neutralize_variable.assert_any_call(
            "employment_income_behavioral_response"
        )

        # Verify inputs set (lines 51-60)
        measurement_branch.set_input.assert_any_call(
            "employment_income_before_lsr", period, 50000
        )

        # Verify branches deleted (lines 71-74) - check they're gone from the dict
        assert "baseline_lsr_measurement" not in baseline_mock.branches
        assert "lsr_measurement" not in simulation.branches

        # Verify cache settings (lines 76-77)
        assert simulation.macro_cache_read == False
        assert simulation.macro_cache_write == False

    # TEST 5: Lines 70, 81-83 - Exception handling and line 70 execution
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.add"
    )
    def test_exception_handling_finally_block(self, mock_add):
        """Test exception handling ensures finally block runs (lines 70, 81-83)."""
        # Simulate exception during calculation
        mock_add.side_effect = ValueError("Test exception")

        person = Mock()
        simulation = Mock()
        baseline = Mock()
        baseline_mock = Mock()
        simulation.baseline = baseline
        simulation._lsr_calculating = False

        # Setup branches for the exception case
        measurement_branch = Mock()
        baseline_branch = Mock()
        baseline_branch.tax_benefit_system.parameters.simulation = Mock()

        # Setup the nested branches structure
        baseline_branches = {"baseline_lsr_measurement": Mock()}
        baseline_mock.branches = baseline_branches
        simulation.branches = {
            "baseline": baseline_mock,
            "lsr_measurement": Mock(),
        }

        # Setup get_branch to return correct branches
        def get_branch_side_effect(name, **kwargs):
            if name == "lsr_measurement":
                return measurement_branch
            elif name == "baseline":
                return baseline_mock

        simulation.get_branch.side_effect = get_branch_side_effect
        baseline_mock.get_branch.return_value = baseline_branch

        # This simulates line 70 - person.simulation might change
        person.simulation = simulation
        person.return_value = 50000

        period = Mock()
        parameters = Mock()

        p = Mock()
        p.elasticities.income = 0.1
        p.elasticities.substitution.all = 0.2
        parameters.return_value.gov.simulation.labor_supply_responses = p

        with pytest.raises(ValueError):
            labor_supply_behavioral_response.formula(
                person, period, parameters
            )

        # Verify finally block executed (line 83)
        assert simulation._lsr_calculating == False

    # TEST 6: Line 70 specifically - simulation reassignment
    @patch(
        "policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response.add"
    )
    def test_simulation_reassignment_line_70(self, mock_add):
        """Test that line 70 reassigns simulation after add() call."""
        # Simulate person.simulation changing during add()
        original_sim = Mock()
        modified_sim = Mock()

        person = Mock()
        # Start with original
        person.simulation = original_sim

        # Setup simulation state
        baseline = Mock()
        baseline_mock = Mock()
        original_sim.baseline = baseline
        original_sim._lsr_calculating = False

        # Setup the nested branches structure for original_sim
        baseline_branches = {"baseline_lsr_measurement": Mock()}
        baseline_mock.branches = baseline_branches
        original_sim.branches = {
            "baseline": baseline_mock,
            "lsr_measurement": Mock(),
        }

        # Setup branches for modified_sim (what we'll switch to)
        modified_baseline_mock = Mock()
        modified_baseline_branches = {"baseline_lsr_measurement": Mock()}
        modified_baseline_mock.branches = modified_baseline_branches
        modified_sim.branches = {
            "baseline": modified_baseline_mock,
            "lsr_measurement": Mock(),
        }

        # Mock branches
        measurement_branch = Mock()
        baseline_branch = Mock()
        baseline_branch.tax_benefit_system.parameters.simulation = Mock()

        # Setup get_branch to return correct branches
        def get_branch_side_effect(name, **kwargs):
            if name == "lsr_measurement":
                return measurement_branch
            elif name == "baseline":
                return baseline_mock

        original_sim.get_branch.side_effect = get_branch_side_effect
        baseline_mock.get_branch.return_value = baseline_branch

        person.return_value = 50000

        # After add(), person.simulation changes (simulating framework behavior)
        def side_effect_add(*args):
            person.simulation = (
                modified_sim  # Simulate framework changing the reference
            )
            return 2000.0

        mock_add.side_effect = side_effect_add

        period = Mock()
        parameters = Mock()
        p = Mock()
        p.elasticities.income = 0.1
        p.elasticities.substitution.all = 0.2
        parameters.return_value.gov.simulation.labor_supply_responses = p

        # Execute
        result = labor_supply_behavioral_response.formula(
            person, period, parameters
        )

        # Line 70 should reassign simulation from person.simulation
        # The deletion should happen on the modified_sim (current person.simulation)
        assert result == 2000.0
        # Verify that branches were deleted from the modified_sim
        assert (
            "baseline_lsr_measurement" not in modified_baseline_mock.branches
        )
        assert "lsr_measurement" not in modified_sim.branches
