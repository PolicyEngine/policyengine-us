from policyengine_us.model_api import *


class co_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "CO TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "co_tanf_eligible"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("co_tanf_grant_standard", period)
        income = spm_unit("co_tanf_countable_income", period)
        return max_(grant_standard - income, 0)



"""
tanf = where(eligible, grant_standard - countable_income, 0)
- tanf_eligible
  - tanf_income_eligible
    - tanf_gross_countable_income
        - tanf_gross_countable_earned_income = sum(p)
        - tanf_gross_countable_unearned_income = sum(p)
    - need standard = f(p, adults, children)
  - tanf_grant_standard = f(p, adults, children)
  - tanf_countable_income
    - tanf_gross_countable_unearned_income
    - tanf_countable_earned_income
      - tanf_gross_countable_earned_income
      - earned income exclusion
"""