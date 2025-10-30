"""
Test if branches properly use neutralized variables during calculations.
"""
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform

# Create a reform that would trigger behavioral responses
SIMPLE_REFORM = {
    "gov.irs.credits.eitc.phase_out_rate[0]": {
        "2024-01-01.2100-12-31": 0.10  # Change something to trigger reform
    }
}

print("Testing if branch calculations use neutralized variables...")

reform = Reform.from_dict(SIMPLE_REFORM, country_id="us")
sim = Microsimulation(reform=reform)

print("✓ Simulation created with reform")
print(f"  Baseline exists: {sim.baseline is not None}")

# Create a branch and neutralize LSR
print("\nCreating branch with neutralized LSR...")
branch = sim.get_branch("test_branch", clone_system=True)
branch.tax_benefit_system.neutralize_variable("employment_income_behavioral_response")
branch.tax_benefit_system.neutralize_variable("labor_supply_behavioral_response")

print("✓ Branch created and LSR neutralized")

# Set employment income input (as LSR does)
emp_before = sim.calculate("employment_income_before_lsr", period=2026)
branch.set_input("employment_income_before_lsr", 2026, emp_before)
print(f"✓ Set employment_income_before_lsr: ${emp_before.sum() / 1e9:.2f}B")

# Now try to calculate employment_income in the branch
print("\nCalculating employment_income in neutralized branch...")
try:
    emp_in_branch = branch.calculate("employment_income", period=2026)
    print(f"✓ SUCCESS! employment_income: ${emp_in_branch.sum() / 1e9:.2f}B")
    print(f"  Should equal employment_income_before_lsr since LSR is neutralized")
    print(f"  Match: {abs(emp_in_branch.sum() - emp_before.sum()) < 1e6}")

except RecursionError:
    print("✗ RecursionError when calculating employment_income in neutralized branch")
    print("This means neutralization isn't being respected in branch calculations")
except Exception as e:
    print(f"✗ Error: {e}")

del sim.branches["test_branch"]
