"""Tests for deterministic take-up variables.

These tests verify that take-up variables which previously used random() now:
1. Use default values correctly in policy calculator mode (no dataset)
2. Can be set explicitly in situations
3. Produce deterministic results
"""

import pytest
from policyengine_us import Simulation


class TestHeadStartTakeUpDefaults:
    """Test that Head Start take-up variables have correct default values."""

    def test_takes_up_head_start_defaults_true(self):
        """Head Start take-up should default to True in policy calculator."""
        sim = Simulation(
            situation={
                "people": {"child": {"age": {2024: 4}}},
                "spm_units": {"spm_unit": {"members": ["child"]}},
                "tax_units": {"tax_unit": {"members": ["child"]}},
                "families": {"family": {"members": ["child"]}},
                "households": {"household": {"members": ["child"]}},
                "marital_units": {"marital_unit": {"members": ["child"]}},
            }
        )
        result = sim.calculate("takes_up_head_start_if_eligible", 2024)
        assert result[0] == True

    def test_takes_up_early_head_start_defaults_true(self):
        """Early Head Start take-up should default to True."""
        sim = Simulation(
            situation={
                "people": {"infant": {"age": {2024: 1}}},
                "spm_units": {"spm_unit": {"members": ["infant"]}},
                "tax_units": {"tax_unit": {"members": ["infant"]}},
                "families": {"family": {"members": ["infant"]}},
                "households": {"household": {"members": ["infant"]}},
                "marital_units": {"marital_unit": {"members": ["infant"]}},
            }
        )
        result = sim.calculate("takes_up_early_head_start_if_eligible", 2024)
        assert result[0] == True


class TestTakeUpExplicitOverrides:
    """Test that take-up variables can be set explicitly."""

    def test_takes_up_head_start_can_be_set_false(self):
        """Head Start take-up can be explicitly set to False."""
        sim = Simulation(
            situation={
                "people": {
                    "child": {
                        "age": {2024: 4},
                        "takes_up_head_start_if_eligible": {2024: False},
                    }
                },
                "spm_units": {"spm_unit": {"members": ["child"]}},
                "tax_units": {"tax_unit": {"members": ["child"]}},
                "families": {"family": {"members": ["child"]}},
                "households": {"household": {"members": ["child"]}},
                "marital_units": {"marital_unit": {"members": ["child"]}},
            }
        )
        result = sim.calculate("takes_up_head_start_if_eligible", 2024)
        assert result[0] == False

    def test_takes_up_early_head_start_can_be_set_false(self):
        """Early Head Start take-up can be explicitly set to False."""
        sim = Simulation(
            situation={
                "people": {
                    "infant": {
                        "age": {2024: 1},
                        "takes_up_early_head_start_if_eligible": {2024: False},
                    }
                },
                "spm_units": {"spm_unit": {"members": ["infant"]}},
                "tax_units": {"tax_unit": {"members": ["infant"]}},
                "families": {"family": {"members": ["infant"]}},
                "households": {"household": {"members": ["infant"]}},
                "marital_units": {"marital_unit": {"members": ["infant"]}},
            }
        )
        result = sim.calculate("takes_up_early_head_start_if_eligible", 2024)
        assert result[0] == False


class TestDeterminism:
    """Test that calculations are deterministic across runs."""

    def test_take_up_variables_are_deterministic(self):
        """Take-up variable calculations should be deterministic."""
        situation = {
            "people": {
                "child": {
                    "age": {2024: 4},
                    "takes_up_head_start_if_eligible": {2024: True},
                }
            },
            "spm_units": {"spm_unit": {"members": ["child"]}},
            "tax_units": {"tax_unit": {"members": ["child"]}},
            "families": {"family": {"members": ["child"]}},
            "households": {"household": {"members": ["child"]}},
            "marital_units": {"marital_unit": {"members": ["child"]}},
        }

        results = []
        for _ in range(3):
            sim = Simulation(situation=situation)
            results.append(
                bool(sim.calculate("takes_up_head_start_if_eligible", 2024)[0])
            )

        # All results should be identical
        assert results[0] == results[1] == results[2]
        assert all(r == True for r in results)
