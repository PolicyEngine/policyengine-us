"""
Test if neutralization works properly in branches.
"""
from policyengine_us import Microsimulation

print("Testing variable neutralization in branches...")

sim = Microsimulation()

# Calculate a variable
print("\n1. Main simulation:")
emp_response_main = sim.calculate("employment_income_behavioral_response", period=2026)
print(f"   employment_income_behavioral_response: ${emp_response_main.sum() / 1e9:.2f}B")

# Create branch and neutralize
print("\n2. Creating branch and neutralizing...")
branch = sim.get_branch("test", clone_system=True)
branch.tax_benefit_system.neutralize_variable("employment_income_behavioral_response")

# Try to calculate in branch
print("3. Calculating in neutralized branch...")
emp_response_branch = branch.calculate("employment_income_behavioral_response", period=2026)
print(f"   employment_income_behavioral_response: ${emp_response_branch.sum() / 1e9:.2f}B")

if emp_response_branch.sum() == 0:
    print("\n✓ Neutralization WORKS - variable returns 0 in branch")
else:
    print(f"\n✗ Neutralization FAILED - variable still returns ${emp_response_branch.sum() / 1e9:.2f}B")

del sim.branches["test"]
