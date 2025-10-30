"""
Test if LSR has proper re-entry guards.
"""
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform

# Simple income elasticity only
SIMPLE_LABOR = {
    "gov.simulation.labor_supply_responses.elasticities.income": {
        "2024-01-01.2100-12-31": -0.05
    }
}

print("Testing LSR for re-entry protection...")

reform = Reform.from_dict(SIMPLE_LABOR, country_id="us")
sim = Microsimulation(reform=reform)

print("✓ Simulation created")
print(f"  Baseline exists: {sim.baseline is not None}")
print(f"  Branches: {list(sim.branches.keys())}")

# Try to directly calculate labor_supply_behavioral_response
print("\nDirectly calculating labor_supply_behavioral_response...")
print("(This is what employment_income_behavioral_response does)")

try:
    # Increase recursion limit to see if it's just depth
    import sys
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(5000)
    print(f"  Increased recursion limit from {old_limit} to 5000")

    lsr = sim.calculate("labor_supply_behavioral_response", period=2026)
    print(f"✓ SUCCESS! LSR calculated: ${lsr.sum() / 1e9:.2f}B")

    sys.setrecursionlimit(old_limit)

except RecursionError as e:
    print("✗ RecursionError even with 5000 recursion limit")
    print("This is infinite recursion, not just deep recursion")
    sys.setrecursionlimit(old_limit)
except Exception as e:
    print(f"✗ Other error: {e}")
    sys.setrecursionlimit(old_limit)
