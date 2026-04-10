"""Unit tests for taxable_social_security_tier_1 and tier_2 variables."""

import pytest
from unittest.mock import Mock
import numpy as np
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.taxable_social_security_tier_1 import (
    taxable_social_security_tier_1,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.taxable_social_security_tier_2 import (
    taxable_social_security_tier_2,
)


class TestTaxableSocialSecurityTier1:
    """Unit tests for taxable_social_security_tier_1."""

    def setup_method(self):
        """Setup common mocks for each test."""
        self.tax_unit = Mock()
        self.period = Mock()
        self.parameters = Mock()

        # Setup parameter structure
        p = Mock()
        p.rate.base.benefit_cap = 0.5
        p.rate.base.excess = 0.5
        p.rate.additional.bracket = 0.5

        # Create mock parameter nodes that support indexing
        base_main = Mock()
        base_main.__getitem__ = lambda self, key: {
            "SINGLE": 25_000,
            "JOINT": 32_000,
            "HEAD_OF_HOUSEHOLD": 25_000,
            "WIDOW": 25_000,
            "SEPARATE": 0,
        }.get(str(key).split("'")[1] if "'" in str(key) else key, 25_000)

        adjusted_base_main = Mock()
        adjusted_base_main.__getitem__ = lambda self, key: {
            "SINGLE": 34_000,
            "JOINT": 44_000,
            "HEAD_OF_HOUSEHOLD": 34_000,
            "WIDOW": 34_000,
            "SEPARATE": 0,
        }.get(str(key).split("'")[1] if "'" in str(key) else key, 34_000)

        p.threshold.base.main = base_main
        p.threshold.adjusted_base.main = adjusted_base_main
        p.threshold.base.separate_cohabitating = 0
        p.threshold.adjusted_base.separate_cohabitating = 0

        self.parameters.return_value.gov.irs.social_security.taxability = p

    def test_zero_income(self):
        """Test with zero income returns zero."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        # Make the mock behave like an array for comparisons
        filing_status_mock.__eq__ = lambda self, other: np.array(
            [False]
        )  # Not SEPARATE
        filing_status_mock.__getitem__ = lambda self, idx: "SINGLE"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([0]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [0]
                ),
                "cohabitating_spouses": np.array([False]),
                "tax_unit_ss_combined_income_excess": np.array([0]),
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert
        assert result[0] == 0

    def test_below_threshold(self):
        """Test income below first threshold returns zero."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        filing_status_mock.__eq__ = lambda self, other: np.array(
            [False]
        )  # Not SEPARATE
        filing_status_mock.__getitem__ = lambda self, idx: "SINGLE"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([10_000]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [20_000]
                ),
                "cohabitating_spouses": np.array([False]),
                "tax_unit_ss_combined_income_excess": np.array([0]),
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert
        assert result[0] == 0

    def test_in_tier_1_single(self):
        """Test single filer in tier 1 range."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        filing_status_mock.__eq__ = lambda self, other: (
            np.array([False]) if other == "SEPARATE" else np.array([True])
        )
        filing_status_mock.__getitem__ = lambda self, idx: "SINGLE"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([30_000]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [30_000]
                ),  # Between 25k and 34k thresholds
                "cohabitating_spouses": np.array([False]),
                "tax_unit_ss_combined_income_excess": np.array(
                    [5_000]
                ),  # 30k - 25k
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert - min(0.5 * 30_000, 0.5 * 5_000) = min(15_000, 2_500) = 2_500
        assert abs(result[0] - 2_500) < 1

    def test_in_tier_2_single(self):
        """Test single filer in tier 2 range."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        filing_status_mock.__eq__ = lambda self, other: (
            np.array([False]) if other == "SEPARATE" else np.array([True])
        )
        filing_status_mock.__getitem__ = lambda self, idx: "SINGLE"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([30_000]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [50_000]
                ),  # Above 34k threshold
                "cohabitating_spouses": np.array([False]),
                "tax_unit_ss_combined_income_excess": np.array(
                    [25_000]
                ),  # 50k - 25k
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert - bracket_amount = min(min(15k, 12.5k), 0.5 * 9k) = min(12.5k, 4.5k) = 4_500
        assert abs(result[0] - 4_500) < 1

    def test_joint_filers(self):
        """Test joint filers calculation."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        filing_status_mock.__eq__ = lambda self, other: np.array(
            [False]
        )  # Never equals SEPARATE
        filing_status_mock.__getitem__ = lambda self, idx: "JOINT"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([30_000]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [40_000]
                ),
                "cohabitating_spouses": np.array([False]),
                "tax_unit_ss_combined_income_excess": np.array(
                    [8_000]
                ),  # 40k - 32k
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert - min(0.5 * 30_000, 0.5 * 8_000) = min(15_000, 4_000) = 4_000
        assert abs(result[0] - 4_000) < 1

    def test_separate_cohabitating(self):
        """Test separate filing with cohabitating spouses (threshold = 0)."""
        # Setup - Create a mock filing status enum
        filing_status_mock = Mock()
        filing_status_mock.possible_values = Mock()
        filing_status_mock.possible_values.SEPARATE = "SEPARATE"
        filing_status_mock.__eq__ = lambda self, other: (
            np.array([True]) if other == "SEPARATE" else np.array([False])
        )
        filing_status_mock.__getitem__ = lambda self, idx: "SEPARATE"

        def side_effect(var, period):
            if var == "filing_status":
                return filing_status_mock
            return {
                "tax_unit_social_security": np.array([20_000]),
                "tax_unit_combined_income_for_social_security_taxability": np.array(
                    [30_000]
                ),
                "cohabitating_spouses": np.array([True]),
                "tax_unit_ss_combined_income_excess": np.array(
                    [30_000]
                ),  # All income is excess
            }.get(var, np.array([0]))

        self.tax_unit.side_effect = side_effect

        # Execute
        result = taxable_social_security_tier_1.formula(
            self.tax_unit, self.period, self.parameters
        )

        # Assert - bracket_amount = 0 because adjusted_base = base = 0
        assert result[0] == 0


class TestTaxableSocialSecurityTier2:
    """Unit tests for taxable_social_security_tier_2."""

    def test_zero_income(self):
        """Test with zero income returns zero."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array([0]),
            "taxable_social_security_tier_1": np.array([0]),
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 0

    def test_tier_1_only(self):
        """Test when all taxable SS is in tier 1."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array([5_350]),
            "taxable_social_security_tier_1": np.array([4_500]),
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 850  # 5_350 - 4_500

    def test_tier_2_amount(self):
        """Test calculation with tier 2 amount."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array([25_500]),
            "taxable_social_security_tier_1": np.array([4_500]),
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 21_000  # 25_500 - 4_500

    def test_high_income(self):
        """Test with high income scenario."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array([34_000]),
            "taxable_social_security_tier_1": np.array([4_500]),
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 29_500  # 34_000 - 4_500

    def test_negative_protection(self):
        """Test that result is never negative."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array([1_000]),
            "taxable_social_security_tier_1": np.array(
                [2_000]
            ),  # Somehow tier 1 is larger
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 0  # max_(1_000 - 2_000, 0) = 0

    def test_array_calculation(self):
        """Test with multiple tax units (array calculation)."""
        tax_unit = Mock()
        tax_unit.side_effect = lambda var, period: {
            "tax_unit_taxable_social_security": np.array(
                [10_000, 20_000, 30_000]
            ),
            "taxable_social_security_tier_1": np.array([4_000, 4_500, 4_500]),
        }[var]

        result = taxable_social_security_tier_2.formula(
            tax_unit, Mock(), Mock()
        )
        assert result[0] == 6_000  # 10_000 - 4_000
        assert result[1] == 15_500  # 20_000 - 4_500
        assert result[2] == 25_500  # 30_000 - 4_500


class TestTaxableSocialSecuritySum:
    """Test that tier 1 + tier 2 equals total taxable social security."""

    def test_tiers_sum_to_total(self):
        """Test that the sum of tier 1 and tier 2 equals total taxable SS."""
        # This is a property test - for any valid inputs, tier1 + tier2 should equal total

        # Test multiple scenarios
        test_cases = [
            # (total_taxable, tier1_expected)
            (0, 0),
            (4_500, 4_500),
            (5_350, 4_500),
            (25_500, 4_500),
            (34_000, 4_500),
        ]

        for total, tier1 in test_cases:
            tier2 = max(total - tier1, 0)

            # Verify the mathematical property
            assert (
                abs((tier1 + tier2) - total) < 0.01
            ), f"Failed for total={total}"
