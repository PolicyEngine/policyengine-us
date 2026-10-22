from policyengine_us.model_api import *


class al_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama interest deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2022/06/21f40.pdf#page=3",
        # Schedule A line 11: qualified mortgage insurance premiums.
        "https://www.revenue.alabama.gov/wp-content/uploads/2022/06/21f40bk.pdf#page=19",
        # Lines 10a-14 use the amount currently allowed for federal purposes.
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/",
        # Code of Alabama Section 40-18-15
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1",
        # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1",
        # 2021 Schedule A (Form 1040)
    )
    defined_for = StateCode.AL

    adds = [
        "mortgage_interest",
        "investment_interest_expense",
        "deductible_mortgage_insurance_premiums",
    ]
