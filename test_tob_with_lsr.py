"""
Test on-model TOB revenue with labor supply responses.
"""
import sys
sys.path.append('/Users/maxghenis/PolicyEngine/crfb-tob-impacts/src')

from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform
from reforms import tax_85_percent_ss

# CBO labor supply elasticities
CBO_LABOR_PARAMS = {
    "gov.simulation.labor_supply_responses.elasticities.income": {
        "2024-01-01.2100-12-31": -0.05
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.1": {
        "2024-01-01.2100-12-31": 0.31
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.2": {
        "2024-01-01.2100-12-31": 0.28
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.3": {
        "2024-01-01.2100-12-31": 0.27
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.4": {
        "2024-01-01.2100-12-31": 0.27
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.5": {
        "2024-01-01.2100-12-31": 0.25
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.6": {
        "2024-01-01.2100-12-31": 0.25
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.7": {
        "2024-01-01.2100-12-31": 0.22
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.8": {
        "2024-01-01.2100-12-31": 0.22
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.9": {
        "2024-01-01.2100-12-31": 0.22
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.primary.10": {
        "2024-01-01.2100-12-31": 0.22
    },
    "gov.simulation.labor_supply_responses.elasticities.substitution.by_position_and_decile.secondary": {
        "2024-01-01.2100-12-31": 0.27
    }
}

print("Testing on-model TOB revenue WITH labor supply responses...")

# Combine Option 2 with LSR
option2_dict = tax_85_percent_ss()
option2_with_lsr = {**option2_dict, **CBO_LABOR_PARAMS}
reform = Reform.from_dict(option2_with_lsr, country_id="us")

print("Creating simulation with Option 2 + LSR...")

try:
    sim = Microsimulation(reform=reform)
    print("✓ Simulation created")

    print("Calculating TOB revenue for 2026...")
    tob_revenue = sim.calculate("tob_revenue_total", period=2026)

    print(f"\n{'='*80}")
    print("SUCCESS!")
    print(f"{'='*80}")
    print(f"TOB revenue (Option 2 with LSR): ${tob_revenue.sum() / 1e9:.2f}B")
    print(f"\nComparison:")
    print(f"  Static (off-model): $110.32B")
    print(f"  Static (on-model):  $109.62B")
    print(f"  Dynamic (on-model): ${tob_revenue.sum() / 1e9:.2f}B")

except Exception as e:
    print(f"\n✗ Calculation failed: {e}")
    import traceback
    traceback.print_exc()
