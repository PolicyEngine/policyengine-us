"""
Test if LSR works at all with CBO parameters.
"""
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform

# Simpler labor params - just income elasticity
SIMPLE_LABOR = {
    "gov.simulation.labor_supply_responses.elasticities.income": {
        "2024-01-01.2100-12-31": -0.05
    }
}

print("Testing basic LSR with simple income elasticity...")

try:
    reform = Reform.from_dict(SIMPLE_LABOR, country_id="us")
    sim = Microsimulation(reform=reform)

    print("✓ Simulation created")
    print("Calculating income_tax...")

    income_tax = sim.calculate("income_tax", period=2026)

    print(f"✓ SUCCESS! LSR works with simple params")
    print(f"  Total income tax: ${income_tax.sum() / 1e9:.2f}B")

except RecursionError as e:
    print(f"✗ RecursionError with simple LSR params")
    print("This means LSR architecture has a fundamental issue")
except Exception as e:
    print(f"✗ Other error: {e}")
    import traceback
    traceback.print_exc()
