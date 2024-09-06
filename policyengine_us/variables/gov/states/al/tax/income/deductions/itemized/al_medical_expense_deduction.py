from policyengine_us.model_api import *


class al_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/"  # Code of Alabama Section 40-18-15, h(13)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1"  # 2021 Schedule A (Form 1040)
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        expense = add(tax_unit, period, ["medical_out_of_pocket_expenses"])
        p = parameters(
            period
        ).gov.states.al.tax.income.deductions.itemized.medical_expense
        medical_floor = p.income_floor * tax_unit("al_agi", period)
        return max_(0, expense - medical_floor)
