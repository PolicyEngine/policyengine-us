from policyengine_us.model_api import *


class ma_claim_of_right_repayment_excluded_from_income(Variable):
    value_type = float
    entity = Person
    label = (
        "Claim of right repayment not included in Massachusetts income when received"
    )
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that was not included in "
        "Massachusetts taxable income in the earlier year it was received. "
        "Massachusetts's claim of right deduction excludes it."
    )
    definition_period = YEAR
    reference = (
        # M.G.L. c. 62, s. 3(B)(a)(14)(i)
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
    )
    defined_for = StateCode.MA
