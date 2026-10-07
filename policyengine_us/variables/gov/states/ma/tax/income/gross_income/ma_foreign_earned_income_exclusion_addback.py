from policyengine_us.model_api import *


class ma_foreign_earned_income_exclusion_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA addition of foreign earned income excluded under section 911"
    unit = USD
    documentation = (
        "Foreign earned income and housing amounts excluded from federal gross "
        "income under 26 U.S.C. 911(a), which Massachusetts adds to gross "
        "income: Form 2555 line 43 (the line 36 housing exclusion plus the "
        "line 42 foreign earned income exclusion, from both spouses' forms on a "
        "joint return). It is not reduced by the line 44 deductions allocable "
        "to the excluded income or by Foreign Earned Income Tax Worksheet line "
        "2b, and it does not include the line 50 housing deduction, which is a "
        "deduction rather than an exclusion. Other income inputs must already "
        "exclude this amount. When not provided, it equals "
        "foreign_earned_income_exclusion, the 911(f) stacking amount on "
        "worksheet line 2c. That default equals line 43 when "
        "Form 2555 lines 44 and 50 and worksheet line 2b are zero, or more "
        "generally when line 50 equals line 44 plus line 2b. An entered "
        "amount, including zero, replaces the default."
    )
    definition_period = YEAR
    reference = (
        # c.62 s.2(a)(1)(C): "Earned income from foreign sources excluded
        # under section nine hundred and eleven of the Code" is added to
        # federal gross income.
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        # Form 1 line 3: compensation excluded under IRC s.911 must be
        # included in line 3 for Massachusetts tax purposes.
        "https://www.mass.gov/doc/2025-form-1-instructions/download#page=10",
        # Form 2555 Part VIII, line 43: lines 36 and 42, before line 44.
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Foreign Earned Income Tax Worksheet lines 2a to 2c.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37",
    )
    defined_for = StateCode.MA
    adds = ["foreign_earned_income_exclusion"]
