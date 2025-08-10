"""
Test script demonstrating UCGID hierarchical functionality.
"""

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
        print(f"CA_23 hierarchical codes: {ca_23_codes}")
        assert ca_23_codes == ["5001800US0623", "0400000US06", "0100000US"]

        # Test State (CA)
        ca = UCGID.CA
        ca_codes = ca.get_hierarchical_codes()
        print(f"CA hierarchical codes: {ca_codes}")
        assert ca_codes == ["0400000US06", "0100000US"]

        # Test US
        us = UCGID.US
        us_codes = us.get_hierarchical_codes()
        print(f"US hierarchical codes: {us_codes}")
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
        assert len(hierarchical_codes) == 1
        assert hierarchical_codes[0] == "0100000US"

        # Test hierarchy matching in simulation context
        is_in_us = ucgid_enum.matches_hierarchy("0100000US")
        assert is_in_us == True
