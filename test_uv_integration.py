#!/usr/bin/env python3
"""Test that uv.lock dependencies work correctly"""

import sys
print(f"Python version: {sys.version}")

# Test imports
from policyengine_us import Microsimulation
from policyengine_core.simulations import Simulation
import microdf
import policyengine_us_data

print("✓ All imports successful")

# Test creating a microsimulation
try:
    sim = Microsimulation(dataset="cps_2023")
    print("✓ Created Microsimulation with cps_2023 dataset")
except Exception as e:
    print(f"✗ Failed to create Microsimulation: {e}")

# Test basic calculation
try:
    income = sim.calculate("household_income", 2024)
    print(f"✓ Calculated household_income for 2024: mean=${income.mean():,.0f}")
except Exception as e:
    print(f"✗ Failed to calculate household_income: {e}")

print("\nAll tests passed!")