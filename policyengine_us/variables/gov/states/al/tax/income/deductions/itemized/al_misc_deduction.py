from policyengine_us.model_api import *


class al_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama Work Related Expense"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/"  # Code of Alabama Section 40-18-15, h(23)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1"  # 2021 Schedule A (Form 1040)
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        misc_expense = add(tax_unit, period, ["misc_deduction"])
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        misc_floor = p.work_related_expense_rate * tax_unit("al_agi", period)
        return max_(0, misc_expense - misc_floor)
