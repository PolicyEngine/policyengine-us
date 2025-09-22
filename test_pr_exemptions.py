#!/usr/bin/env python
"""Test PR exemptions implementation for accuracy"""

from policyengine_us import Simulation

# Create a simulation to test the exemptions
sim = Simulation(
    situation={
        "people": {
            "adult": {
                "age": 30,
                "pr_gross_income_person": 50_000,
            },
            "spouse": {
                "age": 28,
                "pr_gross_income_person": 45_000,
            },
            "student_child": {
                "age": 22,
                "is_full_time_college_student": True,
                "pr_gross_income_person": 5_000,  # Below $7,500 limit
                "pr_is_tax_unit_dependent": True,
            },
            "young_child": {
                "age": 15,
                "pr_gross_income_person": 1_000,  # Below $2,500 limit
                "pr_is_tax_unit_dependent": True,
            },
            "veteran": {
                "age": 65,
                "is_veteran": True,
                "pr_gross_income_person": 2_000,  # Below $2,500 limit
                "pr_is_tax_unit_dependent": True,
            }
        },
        "tax_units": {
            "tax_unit": {
                "members": ["adult", "spouse", "student_child", "young_child", "veteran"],
                "filing_status": "JOINT",
            }
        },
        "households": {
            "household": {
                "members": ["adult", "spouse", "student_child", "young_child", "veteran"],
                "state_code": "PR",
            }
        }
    }
)

# Test personal exemption
personal_exemption = sim.calculate("pr_personal_exemption", 2024)[0]
print(f"Personal Exemption (Joint): ${personal_exemption:,.0f}")
expected_personal = 7_000
assert personal_exemption == expected_personal, f"Expected ${expected_personal:,.0f}, got ${personal_exemption:,.0f}"

# Test dependent eligibility
student_eligible = sim.calculate("pr_eligible_dependent_for_exemption", 2024)[2]
young_eligible = sim.calculate("pr_eligible_dependent_for_exemption", 2024)[3]
veteran_eligible = sim.calculate("pr_eligible_dependent_for_exemption", 2024)[4]

print(f"Student child eligible: {student_eligible}")
print(f"Young child eligible: {young_eligible}")
print(f"Veteran eligible: {veteran_eligible}")

# Test dependent exemption amount
dependent_exemption = sim.calculate("pr_dependents_exemption", 2024)[0]
expected_dependents = 3 * 2_500  # 3 eligible dependents at $2,500 each
print(f"Dependent Exemption: ${dependent_exemption:,.0f}")
assert dependent_exemption == expected_dependents, f"Expected ${expected_dependents:,.0f}, got ${dependent_exemption:,.0f}"

# Test veteran exemption (person-level)
veteran_exemption_person = sim.calculate("pr_veteran_exemption", 2024)[4]  # 5th person (index 4) is the veteran
expected_veteran = 1_500  # 1 veteran at $1,500
print(f"Veteran Exemption (person): ${veteran_exemption_person:,.0f}")
assert veteran_exemption_person == expected_veteran, f"Expected ${expected_veteran:,.0f}, got ${veteran_exemption_person:,.0f}"

# Test with separate filing
sim_separate = Simulation(
    situation={
        "people": {
            "adult": {
                "age": 30,
                "pr_gross_income_person": 50_000,
            },
            "child": {
                "age": 10,
                "pr_gross_income_person": 0,
                "pr_is_tax_unit_dependent": True,
            }
        },
        "tax_units": {
            "tax_unit": {
                "members": ["adult", "child"],
                "filing_status": "SEPARATE",
            }
        },
        "households": {
            "household": {
                "members": ["adult", "child"],
                "state_code": "PR",
            }
        }
    }
)

personal_separate = sim_separate.calculate("pr_personal_exemption", 2024)[0]
print(f"\nPersonal Exemption (Separate): ${personal_separate:,.0f}")
assert personal_separate == 3_500, f"Expected $3,500, got ${personal_separate:,.0f}"

dependent_separate = sim_separate.calculate("pr_dependents_exemption", 2024)[0]
print(f"Dependent Exemption (Separate): ${dependent_separate:,.0f}")
assert dependent_separate == 1_250, f"Expected $1,250, got ${dependent_separate:,.0f}"

print("\n✅ All tests passed!")