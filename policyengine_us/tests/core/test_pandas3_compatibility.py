"""
Tests for pandas 3.0.0 compatibility in policyengine-us.

These tests verify that policyengine-us works correctly with pandas 3.0.0,
which introduces PyArrow-backed strings as default (StringDtype).

These tests will FAIL if policyengine-core < 3.9.1 is used, which doesn't
have the pandas 3 compatibility fixes.
"""

import numpy as np
import pandas as pd

from policyengine_us import Simulation


class TestCoreFilledArrayWithStringDtype:
    """
    Test policyengine-core's filled_array handles pandas StringDtype.

    This directly tests the fix in policyengine-core that converts
    pandas ExtensionDtype to object dtype before calling numpy.full().

    This test WILL FAIL with policyengine-core < 3.9.1.
    """

    def test_filled_array_with_string_dtype(self):
        """
        Test that filled_array handles pandas StringDtype.

        In pandas 3, numpy.full() cannot handle StringDtype, raising:
        TypeError: Cannot interpret '<StringDtype>' as a data type
        """
        from policyengine_core.populations.population import Population
        from policyengine_core.entities import Entity

        entity = Entity(
            key="person",
            plural="people",
            label="Person",
            doc="Test entity",
        )
        population = Population(entity)
        population.count = 5

        # Explicitly use pandas StringDtype - this is what pandas 3 uses by default
        string_dtype = pd.StringDtype()

        # This will fail without the fix:
        # TypeError: Cannot interpret '<StringDtype>' as a data type
        result = population.filled_array("test_value", dtype=string_dtype)

        assert len(result) == 5
        assert all(v == "test_value" for v in result)


class TestCoreVectorialParameterWithStringArray:
    """
    Test policyengine-core's VectorialParameterNodeAtInstant handles StringArray.

    This directly tests the fix that converts pandas StringArray to numpy
    before vectorial parameter lookup.

    This test WILL FAIL with policyengine-core < 3.9.1.
    """

    def test_vectorial_parameter_with_string_array(self):
        """
        Test that vectorial parameter lookup handles pandas StringArray.

        In pandas 3, string operations return StringArray. Parameter lookup
        would fail with: TypeError: unhashable type: 'StringArray'
        """
        from policyengine_core.parameters.vectorial_parameter_node_at_instant import (
            VectorialParameterNodeAtInstant,
        )

        # Create a simple vectorial node
        vector = np.array(
            [(1.0, 2.0)],
            dtype=[("zone_1", "float"), ("zone_2", "float")],
        ).view(np.recarray)

        node = VectorialParameterNodeAtInstant("test", vector, "2024-01-01")

        # Create a pandas StringArray - this is what pandas 3 returns for string ops
        key = pd.array(["zone_1", "zone_2"], dtype="string")

        # This will fail without the fix:
        # TypeError: unhashable type: 'StringArray'
        result = node[key]

        assert len(result) == 2
        np.testing.assert_array_equal(result, [1.0, 2.0])


class TestStateParameterLookupWithPandas3:
    """
    Test that state-based parameter lookup works with pandas 3 StringArray.

    In pandas 3, string columns use StringDtype by default. When looking up
    state-specific parameters using vectorial indexing (e.g.,
    parameters.state.rate[state_code]), the state codes may be StringArray
    instead of numpy array.

    policyengine-core >= 3.9.1 converts StringArray to numpy before lookup.
    """

    def test_state_parameter_lookup(self):
        """
        Test that state-based parameter lookup works for multiple states.

        This exercises the VectorialParameterNodeAtInstant.__getitem__ fix
        that converts pandas StringArray to numpy array.
        """
        # Create a simulation with households in different states
        sim = Simulation(
            situation={
                "people": {
                    "person1": {"age": {"2024": 30}},
                    "person2": {"age": {"2024": 40}},
                },
                "households": {
                    "household1": {
                        "members": ["person1"],
                        "state_code": {"2024": "CA"},
                    },
                    "household2": {
                        "members": ["person2"],
                        "state_code": {"2024": "NY"},
                    },
                },
            }
        )

        # This calculation involves state-based parameter lookups
        # If pandas 3 StringArray handling is broken, this would raise:
        # TypeError: unhashable type: 'StringArray'
        result = sim.calculate("household_net_income", "2024")

        # Basic sanity check - should return an array
        assert isinstance(result, np.ndarray)
        assert len(result) == 2  # Two households


class TestFilledArrayWithStringDtype:
    """
    Test that population.filled_array works with pandas StringDtype.

    In pandas 3, numpy.full() cannot handle StringDtype. policyengine-core
    >= 3.9.1 converts StringDtype to object dtype before calling numpy.full().
    """

    def test_string_variable_default_value(self):
        """
        Test that string-typed variables work correctly.

        Variables with value_type=str use filled_array with a string dtype.
        In pandas 3, this would fail with:
        TypeError: Cannot interpret '<StringDtype>' as a data type
        """
        # Create a simple simulation
        sim = Simulation(
            situation={
                "people": {
                    "person1": {"age": {"2024": 30}},
                },
                "households": {
                    "household1": {
                        "members": ["person1"],
                    },
                },
            }
        )

        # state_code is a string variable - calculating it exercises filled_array
        # with the default value
        result = sim.calculate("state_code", "2024")

        # Should return valid results without error
        assert len(result) == 1


class TestEnumVariableWithPandas3:
    """
    Test that Enum variables work correctly with pandas 3.

    Enum variables involve string-based parameter lookups which can
    trigger the StringArray issue in pandas 3.
    """

    def test_filing_status_enum(self):
        """
        Test that filing_status enum works correctly.
        """
        sim = Simulation(
            situation={
                "people": {
                    "person1": {"age": {"2024": 30}},
                },
                "tax_units": {
                    "tax_unit1": {
                        "members": ["person1"],
                    },
                },
                "households": {
                    "household1": {
                        "members": ["person1"],
                    },
                },
            }
        )

        # filing_status is an enum variable
        result = sim.calculate("filing_status", "2024")

        # Should return valid results
        assert len(result) == 1
