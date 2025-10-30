"""
Test on-model TOB revenue with Option 2 reform.
"""
import sys
sys.path.append('/Users/maxghenis/PolicyEngine/crfb-tob-impacts/src')

from policyengine_us import Microsimulation
from reforms import get_option2_reform

print("Testing on-model TOB revenue with Option 2...")

# Test with Option 2
option2 = get_option2_reform()
sim_option2 = Microsimulation(reform=option2)

print("Calculating for 2026...")

try:
    tob_revenue = sim_option2.calculate("tob_revenue_total", period=2026)
    print(f"✓ Option 2 calculation succeeded!")
    print(f"  Total TOB revenue: ${tob_revenue.sum() / 1e9:.2f}B")
    print(f"\nCompare to our off-model calculation: $110.32B")

    # Also check taxable SS to verify
    taxable_ss = sim_option2.calculate("tax_unit_taxable_social_security", period=2026)
    print(f"\n  Taxable SS under Option 2: ${taxable_ss.sum() / 1e9:.2f}B")

except Exception as e:
    print(f"✗ Calculation failed: {e}")
    import traceback
    traceback.print_exc()
