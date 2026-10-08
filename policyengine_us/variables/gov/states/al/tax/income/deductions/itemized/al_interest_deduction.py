from policyengine_us.model_api import *


class al_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Alabama limits the interest deduction to the amount allowable for "
        "federal income tax purposes, so home mortgage interest on acquisition "
        "debt above the 26 U.S.C. 163(h)(3) limits is not deductible."
    )
    reference = (
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-15",
        # Code of Alabama Section 40-18-15(a)(2)
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=19",
        # 2025 Form 40 instructions, Schedule A lines 10a through 14
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1",
        # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1",
        # 2021 Schedule A (Form 1040)
    )
    defined_for = StateCode.AL

    adds = ["deductible_mortgage_interest", "investment_interest_expense"]
