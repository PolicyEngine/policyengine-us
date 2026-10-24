from policyengine_us.model_api import *


class va_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        # Virginia TANF Manual 305.1 A.2.b
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/tanfview/tanf/Chapter-300---Need-and-Amount-of-Assistance.pdf#page=32",
        # Virginia TANF Manual 305.3 B.3 and B.4
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/tanfview/tanf/Chapter-300---Need-and-Amount-of-Assistance.pdf#page=52",
    )

    def formula(spm_unit, period, parameters):
        gross_earnings = add(spm_unit, period, ["tanf_gross_earned_income"])
        unit_size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.va.dss.tanf.income.deductions.earned
        # Step 1: Apply the standard deduction, which is the SNAP standard
        # deduction for the assistance unit's size (TANF Manual 305.1 A.2.b).
        snap_standard = parameters(period).gov.usda.snap.income.deductions.standard
        state_group = spm_unit.household("state_group_str", period)
        # The SNAP table stops at six members.
        capped_size = clip(unit_size, 1, 6)
        standard_deduction = snap_standard[state_group][capped_size]
        earnings_after_standard = max_(gross_earnings - standard_deduction, 0)
        # Step 2: Apply 20% earned income disregard
        earned_after_20pct = earnings_after_standard * (1 - p.percentage)
        # Step 3: Apply childcare deduction
        childcare_deduction = spm_unit("va_tanf_childcare_deduction", period)
        return max_(earned_after_20pct - childcare_deduction, 0)
