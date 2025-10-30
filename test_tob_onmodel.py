"""
Test on-model TOB revenue calculation.
"""
from policyengine_us import Microsimulation

# Test basic TOB revenue calculation
sim = Microsimulation()

print("Testing on-model TOB revenue variable...")
print("Calculating for 2026...")

try:
    tob_revenue = sim.calculate("tob_revenue_total", period=2026)
    print(f"✓ Calculation succeeded!")
    print(f"  Total TOB revenue: ${tob_revenue.sum() / 1e9:.2f}B")
    print(f"  Mean per tax unit: ${tob_revenue.mean():.2f}")
    print(f"  Median per tax unit: ${tob_revenue.median():.2f}")
except Exception as e:
    print(f"✗ Calculation failed: {e}")
    import traceback
    traceback.print_exc()
