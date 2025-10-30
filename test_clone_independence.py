"""
Test if cloned tax_benefit_system is truly independent.
"""
from policyengine_us import Microsimulation

sim = Microsimulation()

print("Testing tax_benefit_system independence...")

# Create branch with cloned system
branch = sim.get_branch("test", clone_system=True)

print(f"Main TBS id: {id(sim.tax_benefit_system)}")
print(f"Branch TBS id: {id(branch.tax_benefit_system)}")
print(f"Same object: {sim.tax_benefit_system is branch.tax_benefit_system}")

# Neutralize in branch
print("\nNeutralizing employment_income_behavioral_response in branch...")
branch.tax_benefit_system.neutralize_variable("employment_income_behavioral_response")

# Check if it's neutralized in main
emp_var_main = sim.tax_benefit_system.get_variable("employment_income_behavioral_response")
emp_var_branch = branch.tax_benefit_system.get_variable("employment_income_behavioral_response")

print(f"\nMain sim variable neutralized: {emp_var_main.is_neutralized}")
print(f"Branch variable neutralized: {emp_var_branch.is_neutralized}")
print(f"Same variable object: {emp_var_main is emp_var_branch}")

if emp_var_branch.is_neutralized and not emp_var_main.is_neutralized:
    print("\n✓ Tax benefit systems are properly independent")
else:
    print("\n✗ Tax benefit systems are NOT independent - this is the bug!")
