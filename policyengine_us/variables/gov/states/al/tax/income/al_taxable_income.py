from policyengine_us.model_api import *


class al_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama taxable income"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    # The Code of Alabama 1975
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/"  # Code of Alabama Section 40-18-15
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1"  # 2021 Schedule A (Form 1040)
    )

    def formula(tax_unit, period, parameters):
        al_ded = tax_unit("al_deduction", period)
        al_agi = tax_unit("al_agi", period)
        return max_(al_agi - al_ded, 0)
