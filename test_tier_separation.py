"""
Test tier-separated TOB revenue calculations.
"""
import sys
sys.path.append('/Users/maxghenis/PolicyEngine/crfb-tob-impacts/src')

from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform
from reforms import get_option2_reform, tax_85_percent_ss

# CBO labor params
CBO = {
    'gov.simulation.labor_supply_responses.elasticities.income': {'2024-01-01.2100-12-31': -0.05},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.1': {'2024-01-01.2100-12-31': 0.31},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.2': {'2024-01-01.2100-12-31': 0.28},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.3': {'2024-01-01.2100-12-31': 0.27},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.4': {'2024-01-01.2100-12-31': 0.27},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.5': {'2024-01-01.2100-12-31': 0.25},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.6': {'2024-01-01.2100-12-31': 0.25},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.7': {'2024-01-01.2100-12-31': 0.22},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.8': {'2024-01-01.2100-12-31': 0.22},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.9': {'2024-01-01.2100-12-31': 0.22},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.10': {'2024-01-01.2100-12-31': 0.22},
    'gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.secondary': {'2024-01-01.2100-12-31': 0.27}
}

print("="*80)
print("Tier-Separated Trust Fund Revenue - Option 2 with LSR (2026)")
print("="*80)

option2_with_lsr = Reform.from_dict({**tax_85_percent_ss(), **CBO}, country_id='us')
sim = Microsimulation(reform=option2_with_lsr)

print("\n✓ Dynamic simulation created with Option 2 + LSR")

# Calculate tier-separated TOB revenue
print("\nCalculating tier-separated TOB revenue...")

tob_oasdi = sim.calculate('tob_revenue_oasdi', period=2026)
print(f"✓ OASDI (tier 1) TOB revenue: ${tob_oasdi.sum() / 1e9:.2f}B")

tob_medicare = sim.calculate('tob_revenue_medicare_hi', period=2026)
print(f"✓ Medicare HI (tier 2) TOB revenue: ${tob_medicare.sum() / 1e9:.2f}B")

tob_total = sim.calculate('tob_revenue_total', period=2026)
print(f"✓ Total TOB revenue: ${tob_total.sum() / 1e9:.2f}B")

# Verify they sum correctly
expected_total = tob_oasdi.sum() + tob_medicare.sum()
actual_total = tob_total.sum()
diff = abs(expected_total - actual_total)

print(f"\nValidation:")
print(f"  OASDI + Medicare HI = ${expected_total / 1e9:.2f}B")
print(f"  Total variable      = ${actual_total / 1e9:.2f}B")
print(f"  Difference          = ${diff / 1e9:.4f}B")

if diff < 1e6:  # Within $1M
    print("\n✅ Tier separation CORRECT - components sum to total!")
else:
    print(f"\n❌ Tier separation ERROR - difference of ${diff / 1e9:.2f}B")

# Also check tier amounts
tier1_amount = sim.calculate('taxable_social_security_tier_1', period=2026)
tier2_amount = sim.calculate('taxable_social_security_tier_2', period=2026)
total_taxable = sim.calculate('tax_unit_taxable_social_security', period=2026)

print(f"\nTaxable SS amounts:")
print(f"  Tier 1 (OASDI): ${tier1_amount.sum() / 1e9:.2f}B")
print(f"  Tier 2 (Medicare): ${tier2_amount.sum() / 1e9:.2f}B")
print(f"  Total: ${total_taxable.sum() / 1e9:.2f}B")
