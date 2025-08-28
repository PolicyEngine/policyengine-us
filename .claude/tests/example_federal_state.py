# Test case: Federal/state separation violations


# FILE: variables/gov/states/id/liheap/eligible.py
class id_liheap_income_eligible(Variable):
    def formula(person, period, parameters):
        # BAD: Federal percentage hard-coded in state file
        fpg = person("federal_poverty_guideline", period)
        income = person("household_income", period)

        # This 1.5 (150%) is a FEDERAL parameter that should be in
        # parameters/gov/hhs/liheap/income_limit_percentage.yaml
        return income <= fpg * 1.5


# FILE: parameters/gov/states/id/liheap/percentages.yaml
"""
description: Idaho LIHEAP income calculation percentages
values:
  2024-01-01:
    # BAD: These are FEDERAL percentages from 42 USC 8624
    # Should be in parameters/gov/hhs/liheap/
    standard_deduction: 0.52  # 52% from federal law
    earned_income_disregard: 0.20  # 20% from federal law
    
    # GOOD: This is state-specific
    state_adjustment_factor: 1.1  # Idaho adds 10%
"""


# FILE: variables/gov/states/id/tanf/eligible.py
class id_tanf_resources(Variable):
    def formula(person, period, parameters):
        # BAD: Federal TANF resource limit hard-coded
        # Should reference parameters/gov/hhs/tanf/resource_limit.yaml
        return person("resources", period) <= 2000


# Expected issues to find:
# 1. Federal 150% (1.5) hard-coded in state file
# 2. Federal 52% in state parameters
# 3. Federal 20% in state parameters
# 4. Federal $2000 resource limit hard-coded
# Total: 4 federal/state violations
