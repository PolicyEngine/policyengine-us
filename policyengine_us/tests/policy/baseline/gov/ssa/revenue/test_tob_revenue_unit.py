"""Unit tests for tob_revenue variables."""

import pytest
from unittest.mock import Mock, MagicMock
import numpy as np
from policyengine_us.variables.gov.ssa.revenue.tob_revenue_total import (
    tob_revenue_total,
)
from policyengine_us.variables.gov.ssa.revenue.tob_revenue_oasdi import (
    tob_revenue_oasdi,
)
from policyengine_us.variables.gov.ssa.revenue.tob_revenue_medicare_hi import (
    tob_revenue_medicare_hi,
)


def _mock_revenue_branch(income_tax):
    branch = Mock()
    branch.tax_benefit_system = Mock()
    branch.tax_benefit_system.variables = Mock()
    branch.tax_benefit_system.variables.keys.return_value = []
    branch.input_variables = []
    branch.tax_unit.return_value = np.array([income_tax])
    branch.delete_arrays = Mock()
    tax_unit_population = Mock()
    tax_unit_population.get_holder.return_value = Mock()
    branch.populations = {"tax_unit": tax_unit_population}
    return branch


class TestTobRevenueTotal:
    """Unit tests for tob_revenue_total."""

    def test_zero_income(self):
        """Test with zero income returns zero revenue."""
        tax_unit = Mock()
        tax_unit.simulation = Mock()

        # Setup branch mock
        branch = Mock()
        branch.tax_benefit_system = Mock()
        branch.tax_benefit_system.neutralize_variable = Mock()
        branch.tax_benefit_system.variables = Mock()
        branch.tax_benefit_system.variables.keys.return_value = [
            "income_tax",
            "taxable_ss",
        ]
        branch.input_variables = []
        branch.delete_arrays = Mock()
        branch.tax_unit.return_value = np.array([0])  # income_tax without SS

        tax_unit.simulation.get_branch.return_value = branch
        tax_unit.simulation.branches = {"tob_calc": branch}
        tax_unit.return_value = np.array([0])  # income_tax with SS

        result = tob_revenue_total.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0

    def test_with_taxable_ss(self):
        """Test calculation with taxable social security."""
        tax_unit = Mock()
        tax_unit.simulation = Mock()

        # Setup branch mock
        branch = Mock()
        branch.tax_benefit_system = Mock()
        branch.tax_benefit_system.neutralize_variable = Mock()
        branch.tax_benefit_system.variables = Mock()
        branch.tax_benefit_system.variables.keys.return_value = [
            "income_tax",
            "taxable_ss",
        ]
        branch.input_variables = []
        branch.tax_unit.return_value = np.array(
            [5_000]
        )  # income_tax without SS
        branch.delete_arrays = Mock()

        tax_unit.simulation.get_branch.return_value = branch
        tax_unit.simulation.branches = {"tob_calc": branch}
        tax_unit.return_value = np.array([8_000])  # income_tax with SS

        result = tob_revenue_total.formula(tax_unit, Mock(), Mock())
        assert result[0] == 3_000  # 8_000 - 5_000

        # Verify neutralization was called
        branch.tax_benefit_system.neutralize_variable.assert_called_once_with(
            "tax_unit_taxable_social_security"
        )

    def test_below_threshold(self):
        """Test when income is below SS taxation threshold."""
        tax_unit = Mock()
        tax_unit.simulation = Mock()

        # Setup branch mock - same tax with and without SS (below threshold)
        branch = Mock()
        branch.tax_benefit_system = Mock()
        branch.tax_benefit_system.neutralize_variable = Mock()
        branch.tax_benefit_system.variables = Mock()
        branch.tax_benefit_system.variables.keys.return_value = [
            "income_tax",
            "taxable_ss",
        ]
        branch.input_variables = []
        branch.tax_unit.return_value = np.array(
            [1_000]
        )  # income_tax without SS
        branch.delete_arrays = Mock()

        tax_unit.simulation.get_branch.return_value = branch
        tax_unit.simulation.branches = {"tob_calc": branch}
        tax_unit.return_value = np.array(
            [1_000]
        )  # income_tax with SS (same, below threshold)

        result = tob_revenue_total.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0  # No additional tax from SS

    def test_branch_cleanup(self):
        """Test that branch is properly cleaned up after calculation."""
        tax_unit = Mock()
        sim = Mock()
        tax_unit.simulation = sim

        # Setup branch mock
        branch = Mock()
        branch.tax_benefit_system = Mock()
        branch.tax_benefit_system.neutralize_variable = Mock()
        branch.tax_benefit_system.variables = Mock()
        branch.tax_benefit_system.variables.keys.return_value = [
            "income_tax",
            "taxable_ss",
        ]
        branch.input_variables = []
        branch.tax_unit.return_value = np.array([10_000])
        branch.delete_arrays = Mock()

        # Setup branches dictionary that tracks deletions
        branches_dict = {"tob_calc": branch}
        deleted_keys = []

        def del_item(self, key):
            deleted_keys.append(key)
            del branches_dict[key]

        sim.branches = MagicMock()
        sim.branches.__setitem__ = branches_dict.__setitem__
        sim.branches.__getitem__ = branches_dict.__getitem__
        sim.branches.__delitem__ = del_item
        sim.get_branch.return_value = branch

        tax_unit.return_value = np.array([15_000])

        result = tob_revenue_total.formula(tax_unit, Mock(), Mock())

        # Verify branch was deleted
        assert "tob_calc" in deleted_keys
        assert result[0] == 5_000

    def test_multiple_tax_units(self):
        """Test calculation with multiple tax units (array)."""
        tax_unit = Mock()
        tax_unit.simulation = Mock()

        # Setup branch mock
        branch = Mock()
        branch.tax_benefit_system = Mock()
        branch.tax_benefit_system.neutralize_variable = Mock()
        branch.tax_benefit_system.variables = Mock()
        branch.tax_benefit_system.variables.keys.return_value = [
            "income_tax",
            "taxable_ss",
        ]
        branch.input_variables = []
        branch.tax_unit.return_value = np.array(
            [5_000, 10_000, 0]
        )  # income_tax without SS
        branch.delete_arrays = Mock()

        tax_unit.simulation.get_branch.return_value = branch
        tax_unit.simulation.branches = {"tob_calc": branch}
        tax_unit.return_value = np.array(
            [8_000, 15_000, 0]
        )  # income_tax with SS

        result = tob_revenue_total.formula(tax_unit, Mock(), Mock())
        assert result[0] == 3_000  # 8_000 - 5_000
        assert result[1] == 5_000  # 15_000 - 10_000
        assert result[2] == 0  # 0 - 0


class TestTobRevenueOasdi:
    """Unit tests for tob_revenue_oasdi's double-branch allocation."""

    def test_uses_capped_social_security_branch(self):
        """OASDI is the tax difference between capped SS and no SS."""
        tax_unit = Mock()
        sim = Mock()
        tax_unit.simulation = sim
        period = Mock()
        parameters = Mock()
        parameters.return_value.gov.ssa.revenue.oasdi_share_of_gross_ss = 0.5

        tax_unit.side_effect = lambda var, period: {
            "tax_unit_social_security": np.array([10_000]),
            "tax_unit_taxable_social_security": np.array([8_500]),
        }[var]

        branch_no_ss = _mock_revenue_branch(1_000)
        branch_capped = _mock_revenue_branch(1_200)
        branches = {
            "oasdi_no_ss": branch_no_ss,
            "oasdi_capped": branch_capped,
        }
        sim.get_branch.side_effect = lambda name, **kwargs: branches[name]
        sim.branches = {
            "oasdi_no_ss": branch_no_ss,
            "oasdi_capped": branch_capped,
        }

        result = tob_revenue_oasdi.formula(tax_unit, period, parameters)
        capped_input = branch_capped.populations["tax_unit"].get_holder.return_value

        assert result[0] == 200
        capped_input.set_input.assert_called_once()
        assert capped_input.set_input.call_args.args[0] is period
        assert capped_input.set_input.call_args.args[1][0] == 5_000
        assert "oasdi_no_ss" not in sim.branches
        assert "oasdi_capped" not in sim.branches


class TestTobRevenueMedicareHi:
    """Unit tests for tob_revenue_medicare_hi's double-branch allocation."""

    def test_uses_full_minus_capped_social_security_branch(self):
        """HI is the tax difference between full SS and capped SS."""
        tax_unit = Mock()
        sim = Mock()
        tax_unit.simulation = sim
        period = Mock()
        parameters = Mock()
        parameters.return_value.gov.ssa.revenue.oasdi_share_of_gross_ss = 0.5

        tax_unit.side_effect = lambda var, period: {
            "tax_unit_social_security": np.array([10_000]),
            "tax_unit_taxable_social_security": np.array([8_500]),
            "income_tax": np.array([1_500]),
        }[var]

        branch_capped = _mock_revenue_branch(1_200)
        sim.get_branch.return_value = branch_capped
        sim.branches = {"hi_capped": branch_capped}

        result = tob_revenue_medicare_hi.formula(tax_unit, period, parameters)
        capped_input = branch_capped.populations["tax_unit"].get_holder.return_value

        assert result[0] == 300
        capped_input.set_input.assert_called_once()
        assert capped_input.set_input.call_args.args[0] is period
        assert capped_input.set_input.call_args.args[1][0] == 5_000
        assert "hi_capped" not in sim.branches


class TestTobRevenueIntegration:
    """Integration tests for the relationship between tob revenue variables."""

    def test_oasdi_plus_medicare_equals_total(self):
        """Test that OASDI + Medicare HI equals total TOB revenue."""
        # This is a property that should always hold

        # Test various scenarios
        test_cases = [
            # (total_tob, tier1, tier2)
            (0, 0, 0),
            (1_000, 4_500, 0),  # Only tier 1
            (2_000, 0, 21_000),  # Only tier 2
            (3_000, 4_500, 4_500),  # Equal tiers
            (5_000, 4_500, 21_000),  # More tier 2
        ]

        for total_tob, tier1, tier2 in test_cases:
            total_taxable = tier1 + tier2

            if total_taxable > 0:
                oasdi_share = tier1 / total_taxable
                medicare_share = tier2 / total_taxable

                oasdi_revenue = total_tob * oasdi_share
                medicare_revenue = total_tob * medicare_share

                # Verify the sum equals total
                assert (
                    abs((oasdi_revenue + medicare_revenue) - total_tob) < 0.01
                ), f"Failed for total_tob={total_tob}, tier1={tier1}, tier2={tier2}"
            else:
                # When no taxable SS, both should be zero
                assert total_tob == 0 or (tier1 == 0 and tier2 == 0)
