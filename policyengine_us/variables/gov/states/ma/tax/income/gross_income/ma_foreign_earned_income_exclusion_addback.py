from policyengine_us.model_api import *


class ma_foreign_earned_income_exclusion_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA addition of foreign earned income excluded under section 911"
    unit = USD
    documentation = (
        "Foreign earned income and housing amounts excluded from federal gross "
        "income under 26 U.S.C. 911(a), which Massachusetts adds back to gross "
        "income: Form 2555 line 43 (the housing exclusion on line 36 plus the "
        "foreign earned income exclusion on line 42, both spouses' forms on a "
        "joint return), before the line 44 deductions allocable to the "
        "excluded income. It leaves out the section 911(c)(4) housing "
        "deduction (line 50), which is not an exclusion, and the itemized "
        "deductions netted out of the federal 911(f) stacking amount. Other "
        "income inputs are the amounts left after the exclusion. When not "
        "provided, it equals foreign_earned_income_exclusion, the 911(f) "
        "stacking amount (Foreign Earned Income Tax Worksheet line 2c), which "
        "is exact only when Form 2555 lines 44 and 50 and worksheet line 2b "
        "are zero. An entered amount, including zero, replaces that default."
    )
    definition_period = YEAR
    reference = (
        # c.62 s.2(a)(1)(C): "Earned income from foreign sources excluded
        # under section nine hundred and eleven of the Code" is added to
        # federal gross income.
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        # Form 2555 Part VIII, line 43: lines 36 and 42, before line 44.
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Foreign Earned Income Tax Worksheet lines 2a to 2c.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37",
    )
    defined_for = StateCode.MA
    adds = ["foreign_earned_income_exclusion"]
