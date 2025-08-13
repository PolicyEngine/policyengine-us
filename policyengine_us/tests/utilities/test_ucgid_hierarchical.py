"""
Test script demonstrating UCGID hierarchical functionality.
"""

import numpy as np
from policyengine_us import Microsimulation
from policyengine_us.variables.household.demographic.geographic.ucgid.ucgid_enum import (
    UCGID,
)


class TestUCGIDHierarchical:
    """Test class for UCGID hierarchical functionality."""

    def test_ucgid_enum_hierarchical_methods(self):
        """Test the hierarchical methods on UCGID enum values directly."""
        print("\n=== Testing UCGID Enum Hierarchical Methods ===")

        # Test Congressional District (CA_23)
        ca_23 = UCGID.CA_23
        ca_23_codes = ca_23.get_hierarchical_codes()
        assert ca_23_codes == ["5001800US0623", "0400000US06", "0100000US"]

        # Test State (CA)
        ca = UCGID.CA
        ca_codes = ca.get_hierarchical_codes()
        assert ca_codes == ["0400000US06", "0100000US"]

        # Test US
        us = UCGID.US
        us_codes = us.get_hierarchical_codes()
        assert us_codes == ["0100000US"]

        # Test hierarchy matching
        assert ca_23.matches_hierarchy("0400000US06") == True
        assert ca_23.matches_hierarchy("0100000US") == True
        assert ca.matches_hierarchy("5001800US0623") == False

    def test_ucgid_simulation_usage(self):
        """Test how UCGID is used in a PolicyEngine simulation."""
        simulation = Microsimulation()
        ucgid_values = simulation.calculate("ucgid", "2024")

        # The UCGID value should be a string (enum name)
        ucgid_string = ucgid_values.iloc[0]  # First household
        assert type(ucgid_string) == str

        # Convert the string back to enum to access hierarchical methods
        ucgid_enum = UCGID[ucgid_string]
        hierarchical_codes = ucgid_enum.get_hierarchical_codes()

        # Should have 2 hierarchical codes for state-level UCGIDs: [state, US]
        assert len(hierarchical_codes) == 2
        assert (
            hierarchical_codes[1] == "0100000US"
        )  # Second code should always be US
        assert hierarchical_codes[0].startswith(
            "0400000US"
        )  # First should be state-level

        # Test hierarchy matching in simulation context
        is_in_us = ucgid_enum.matches_hierarchy("0100000US")
        assert is_in_us == True

    def test_ucgid_str_variable(self):
        """Test the UCGID string variable functionality."""
        simulation = Microsimulation()
        ucgid_str_values = simulation.calculate("ucgid_str", "2024")

        # The UCGID string variable should return a string representation
        ucgid_str = ucgid_str_values.iloc[0]
        assert type(ucgid_str) == str
        assert (
            ucgid_str.startswith("0100000US")
            | ucgid_str.startswith("0400000US")
            | ucgid_str.startswith("5001800US")
        )

        # Create a basic simulation to test with specific input values
        from policyengine_us import Simulation

        simulation = Simulation(
            situation={
                "people": {"person": {}},
                "households": {"household": {"members": ["person"]}},
            }
        )

        # Set a specific UCGID value for testing (CA_23)
        simulation.set_input("ucgid", 2024, UCGID.CA_23)

        # Calculate the ucgid_str value
        ucgid_str_values = simulation.calculate("ucgid_str", 2024)
        ucgid_str = ucgid_str_values[0]

        # Verify it contains all three hierarchical codes
        assert ucgid_str == "5001800US0623,0400000US06,0100000US"

    def test_ucgid_microsimulation_input_override(self):
        """Test setting UCGID input for all households in a microsimulation."""
        microsim = Microsimulation()

        # Get initial values
        ucgid_before = microsim.calculate("ucgid", 2024)
        num_households = len(ucgid_before)

        # Set all households to CA_23
        input_array = np.array([UCGID.CA_23] * num_households)
        microsim.set_input("ucgid", 2024, input_array)

        # Verify the input was set
        ucgid_after = microsim.calculate("ucgid", 2024)
        after_values = ucgid_after.values
        assert all(val == "CA_23" for val in after_values)
        assert len(set(after_values)) == 1

        # Test that ucgid_str now returns hierarchical codes for all households
        ucgid_str_values = microsim.calculate("ucgid_str", 2024)
        expected_str = "5001800US0623,0400000US06,0100000US"
        str_values = ucgid_str_values.values
        assert all(str_val == expected_str for str_val in str_values)
