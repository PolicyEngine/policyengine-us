from policyengine_us.model_api import *


class al_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/"  # Code of Alabama Section 40-18-15
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1"  # 2021 Schedule A (Form 1040)
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        itm_ded = tax_unit("al_itemized_deductions", period)
        std_ded = tax_unit("al_standard_deduction", period)
        al_ded = max_(itm_ded, std_ded)
        per_exm = tax_unit("al_personal_exemption", period)
        dep_exm = tax_unit("al_dependent_exemption", period)
        return al_ded + per_exm + dep_exm
