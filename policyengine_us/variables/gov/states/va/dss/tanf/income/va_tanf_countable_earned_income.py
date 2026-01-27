from policyengine_us.model_api import *


class va_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=55"

    def formula(spm_unit, period, parameters):
        gross_earnings = add(spm_unit, period, ["tanf_gross_earned_income"])
        unit_size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.va.dss.tanf.income.deductions.earned
        # Step 1: Apply flat deduction by unit size
        flat_exclusion = p.flat.calc(unit_size)
        earnings_after_flat = max_(gross_earnings - flat_exclusion, 0)
        # Step 2: Apply 20% earned income disregard
        earned_after_20pct = earnings_after_flat * (1 - p.percentage)
        # Step 3: Apply childcare deduction
        childcare_deduction = spm_unit("va_tanf_childcare_deduction", period)
        return max_(earned_after_20pct - childcare_deduction, 0)
