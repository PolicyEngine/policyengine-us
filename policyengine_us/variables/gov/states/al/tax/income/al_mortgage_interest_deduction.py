from policyengine_us.model_api import *


class al_mortgage_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama mortgage interest deduction"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"
    )