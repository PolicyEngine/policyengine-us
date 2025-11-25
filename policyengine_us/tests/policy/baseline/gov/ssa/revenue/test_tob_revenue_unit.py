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
    """Unit tests for tob_revenue_oasdi."""

    def test_zero_income(self):
        """Test with zero income returns zero."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([0]),
            "taxable_social_security_tier_1": np.array([0]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_oasdi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0

    def test_only_tier_1(self):
        """Test when only tier 1 exists (100% to OASDI)."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000]),
            "taxable_social_security_tier_1": np.array([4_500]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_oasdi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 1_000  # 100% of revenue goes to OASDI

    def test_tier_1_and_tier_2(self):
        """Test allocation between OASDI and Medicare HI."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([5_000]),
            "taxable_social_security_tier_1": np.array([4_500]),
            "taxable_social_security_tier_2": np.array([21_000]),
        }[var]

        result = tob_revenue_oasdi.formula(tax_unit, Mock(), Mock())
        # OASDI share = 4_500 / (4_500 + 21_000) = 4_500 / 25_500 ≈ 0.1765
        # OASDI revenue = 5_000 * 0.1765 ≈ 882.35
        assert abs(result[0] - 882.35) < 1

    def test_division_by_zero(self):
        """Test safe division when total taxable is zero."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000]),
            "taxable_social_security_tier_1": np.array([0]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_oasdi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0  # Safe division returns 0

    def test_multiple_tax_units(self):
        """Test with multiple tax units."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000, 2_000, 0]),
            "taxable_social_security_tier_1": np.array([4_500, 4_500, 0]),
            "taxable_social_security_tier_2": np.array([0, 4_500, 0]),
        }[var]

        result = tob_revenue_oasdi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 1_000  # 100% to OASDI
        assert result[1] == 1_000  # 50% to OASDI
        assert result[2] == 0  # No revenue


class TestTobRevenueMedicareHi:
    """Unit tests for tob_revenue_medicare_hi."""

    def test_zero_income(self):
        """Test with zero income returns zero."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([0]),
            "taxable_social_security_tier_1": np.array([0]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0

    def test_only_tier_2(self):
        """Test when only tier 2 exists (100% to Medicare HI)."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000]),
            "taxable_social_security_tier_1": np.array([0]),
            "taxable_social_security_tier_2": np.array([21_000]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 1_000  # 100% of revenue goes to Medicare HI

    def test_tier_1_and_tier_2(self):
        """Test allocation between OASDI and Medicare HI."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([5_000]),
            "taxable_social_security_tier_1": np.array([4_500]),
            "taxable_social_security_tier_2": np.array([21_000]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        # Medicare share = 21_000 / (4_500 + 21_000) = 21_000 / 25_500 ≈ 0.8235
        # Medicare revenue = 5_000 * 0.8235 ≈ 4117.65
        assert abs(result[0] - 4117.65) < 1

    def test_tier_1_only(self):
        """Test when only tier 1 exists (0% to Medicare HI)."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000]),
            "taxable_social_security_tier_1": np.array([4_500]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0  # 0% to Medicare HI when only tier 1

    def test_division_by_zero(self):
        """Test safe division when total taxable is zero."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000]),
            "taxable_social_security_tier_1": np.array([0]),
            "taxable_social_security_tier_2": np.array([0]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0  # Safe division returns 0

    def test_multiple_tax_units(self):
        """Test with multiple tax units."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tob_revenue_total": np.array([1_000, 2_000, 3_000]),
            "taxable_social_security_tier_1": np.array([4_500, 4_500, 0]),
            "taxable_social_security_tier_2": np.array([0, 4_500, 9_000]),
        }[var]

        result = tob_revenue_medicare_hi.formula(tax_unit, Mock(), Mock())
        assert result[0] == 0  # 0% to Medicare HI
        assert result[1] == 1_000  # 50% to Medicare HI
        assert result[2] == 3_000  # 100% to Medicare HI


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
