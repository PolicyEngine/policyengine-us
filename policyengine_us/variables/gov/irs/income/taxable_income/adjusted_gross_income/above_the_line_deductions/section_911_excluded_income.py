from policyengine_us.model_api import *


class section_911_excluded_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income excluded or deducted under section 911"
    unit = USD
    documentation = (
        "Foreign earned income and housing amounts excluded from gross income "
        "under 26 U.S.C. 911, plus the section 911(c)(4) foreign housing "
        "deduction: Form 2555 lines 45 and 50 (both spouses' forms on a joint "
        "return). Modified adjusted gross incomes add this amount back. It is "
        "larger than foreign_earned_income_exclusion, the amount the section "
        "911(f) rate stacking uses, by any deductions disallowed because they "
        "relate to the excluded income. When not provided, it equals "
        "foreign_earned_income_exclusion, which is exact when no deductions "
        "are disallowed."
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
    )
    adds = ["foreign_earned_income_exclusion"]
