from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import SECTION_911_LEAF_INPUTS


class section_911_excluded_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income excluded or deducted under section 911"
    unit = USD
    documentation = (
        "Foreign earned income and housing amounts excluded from gross income "
        "under 26 U.S.C. 911, plus the section 911(c)(4) foreign housing "
        "deduction: Form 2555 lines 45 and 50 (both spouses' forms on a joint "
        "return). Modified adjusted gross incomes add this amount back, before "
        "the federal stacking worksheet subtracts disallowed deductions and "
        "floors its result at zero. Applicable Form 2555 leaves determine this "
        "amount, preserving a negative line 45. Without those leaves, the "
        "legacy foreign_earned_income_exclusion amount is the fallback; it "
        "cannot reconstruct the pre-worksheet amount."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/911",
        # Schedule 8812 line 2b, Schedule 1-A lines 2b and 2c, Form 8936
        # lines 1c and 1d: the modified AGI add-back is Form 2555 lines 45
        # and 50.
        "https://www.irs.gov/pub/irs-prior/f1040s8--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f1040s1a--2025.pdf#page=1",
        # The Foreign Earned Income Tax Worksheet subtracts the disallowed
        # deductions from the same amount (lines 2a to 2c).
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37",
        # Publication 54's deduction example 4 reports a negative line 45.
        "https://www.irs.gov/publications/p54",
    )

    def formula(tax_unit, period, parameters):
        has_leaf_inputs = any(
            input_period.start <= period.start
            for variable in SECTION_911_LEAF_INPUTS
            for input_period in tax_unit.simulation._get_exportable_input_periods(
                variable, include_computed_variables=False
            )
        )
        if not has_leaf_inputs:
            return tax_unit("foreign_earned_income_exclusion", period)

        gross = tax_unit("foreign_earned_income_exclusion_gross", period)
        allocable_deductions = tax_unit(
            "foreign_earned_income_exclusion_allocable_deductions", period
        )
        housing_deduction = tax_unit("foreign_housing_deduction", period)
        return gross - allocable_deductions + housing_deduction
