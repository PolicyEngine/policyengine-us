"""
Test if calculations in a branch actually respect neutralizations.
"""
from policyengine_us import Microsimulation
import sys
sys.path.append('/Users/maxghenis/PolicyEngine/crfb-tob-impacts/src')
from reforms import get_option2_reform

print("Testing if branch calculations respect neutralizations...")

# Use Option 2 to have a real reform
sim = Microsimulation(reform=get_option2_reform())

print("✓ Created simulation with Option 2")
print(f"  Baseline exists: {sim.baseline is not None}")

# Create branch and neutralize
branch = sim.get_branch("test", clone_system=True)
branch.tax_benefit_system.neutralize_variable("employment_income_behavioral_response")

print("✓ Created branch and neutralized employment_income_behavioral_response")

# Try to calculate employment_income in the branch
print("\nCalculating employment_income in branch...")
print("  (should just use employment_income_before_lsr since behavioral response is neutralized)")

try:
    emp = branch.calculate("employment_income", period=2026)
    print(f"✓ SUCCESS! employment_income calculated: ${emp.sum() / 1e9:.2f}B")

    # Check if behavioral response was actually neutralized
    emp_response = branch.calculate("employment_income_behavioral_response", period=2026)
    print(f"  employment_income_behavioral_response in branch: ${emp_response.sum() / 1e9:.2f}B")

    if emp_response.sum() == 0:
        print("\n✓ Neutralization WORKS in branch calculations!")
    else:
        print(f"\n✗ Neutralization FAILED - got ${emp_response.sum() / 1e9:.2f}B instead of 0")

except RecursionError:
    print("✗ RecursionError - branch calculations don't respect neutralization")
    print("This is a BUG in policyengine-core!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
