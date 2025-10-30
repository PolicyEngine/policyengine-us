"""
Debug LSR branch creation to find where recursion starts.
"""
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform

# Simple LSR
SIMPLE_LABOR = {
    "gov.simulation.labor_supply_responses.elasticities.income": {
        "2024-01-01.2100-12-31": -0.05
    }
}

print("Testing LSR branch creation step by step...")

reform = Reform.from_dict(SIMPLE_LABOR, country_id="us")
sim = Microsimulation(reform=reform)

print("✓ Simulation created")
print(f"  sim.baseline exists: {sim.baseline is not None}")
print(f"  sim.branches: {list(sim.branches.keys())}")

# Try to manually do what LSR does
print("\nManually creating LSR measurement branch...")

try:
    # This is what labor_supply_behavioral_response does
    measurement_branch = sim.get_branch("lsr_measurement", clone_system=True)
    print("✓ measurement_branch created")

    # Neutralize as LSR does
    measurement_branch.tax_benefit_system.neutralize_variable("employment_income_behavioral_response")
    measurement_branch.tax_benefit_system.neutralize_variable("self_employment_income_behavioral_response")
    print("✓ Variables neutralized")

    # Set inputs as LSR does
    emp_before_lsr = sim.calculate("employment_income_before_lsr", period=2026)
    print(f"✓ Got employment_income_before_lsr from main sim: ${emp_before_lsr.sum() / 1e9:.2f}B")

    measurement_branch.set_input("employment_income_before_lsr", 2026, emp_before_lsr)
    print("✓ Set input in branch")

    # Now try to calculate household_net_income in the branch (this is what relative_income_change does)
    print("\nCalculating household_net_income in measurement_branch...")
    measurement_person = measurement_branch.populations["person"]
    net_income = measurement_person.household("household_net_income", 2026)

    print(f"✓ SUCCESS! household_net_income calculated: ${net_income.sum() / 1e9:.2f}B")

except RecursionError as e:
    print("✗ RecursionError during manual LSR setup")
    print("The issue is in how LSR sets up its branches")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
