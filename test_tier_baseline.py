"""
Test tier separation in baseline.
"""
from policyengine_us import Microsimulation

print("Testing tier separation in BASELINE...")

sim = Microsimulation()

# Check tier amounts
tier1 = sim.calculate('taxable_social_security_tier_1', period=2026)
tier2 = sim.calculate('taxable_social_security_tier_2', period=2026)
total = sim.calculate('tax_unit_taxable_social_security', period=2026)

print(f"\nTaxable SS amounts (baseline):")
print(f"  Tier 1 (0-50%, OASDI): ${tier1.sum() / 1e9:.2f}B")
print(f"  Tier 2 (50-85%, Medicare): ${tier2.sum() / 1e9:.2f}B")
print(f"  Total: ${total.sum() / 1e9:.2f}B")
print(f"  Sum of tiers: ${(tier1.sum() + tier2.sum()) / 1e9:.2f}B")

# Calculate tier-separated TOB revenue
print("\nCalculating tier-separated TOB revenue...")

tob_oasdi = sim.calculate('tob_revenue_oasdi', period=2026)
print(f"  OASDI (tier 1) TOB: ${tob_oasdi.sum() / 1e9:.2f}B")

tob_medicare = sim.calculate('tob_revenue_medicare_hi', period=2026)
print(f"  Medicare HI (tier 2) TOB: ${tob_medicare.sum() / 1e9:.2f}B")

tob_total = sim.calculate('tob_revenue_total', period=2026)
print(f"  Total TOB: ${tob_total.sum() / 1e9:.2f}B")

# Check if they sum
expected = tob_oasdi.sum() + tob_medicare.sum()
actual = tob_total.sum()
print(f"\nValidation:")
print(f"  OASDI + Medicare = ${expected / 1e9:.2f}B")
print(f"  Total variable   = ${actual / 1e9:.2f}B")
print(f"  Match: {abs(expected - actual) < 1e6}")
