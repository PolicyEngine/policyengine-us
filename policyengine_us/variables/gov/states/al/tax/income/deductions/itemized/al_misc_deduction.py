from policyengine_us.model_api import *


class al_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama Work Related Expense"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/",  # Code of Alabama Section 40-18-15, h(23)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1",  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1",  # 2021 Schedule A (Form 1040)
        # 2024 Form 40 instructions, Schedule A lines 20 to 24.
        "https://www.revenue.alabama.gov/wp-content/uploads/2025/01/24f40bk.pdf#page=20",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        # Ala. Code 40-18-15(a)(23) allows unreimbursed employee business
        # expenses and section 212 expenses above 2% of Alabama AGI. Alabama
        # kept this deduction after the federal suspension (26 U.S.C. 67(g)),
        # so start from the expenses, not the federal misc_deduction, which is
        # zero from 2018 and already net of the federal 2% floor.
        misc_expense = tax_unit("total_misc_deductions", period)
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        misc_floor = p.work_related_expense_rate * tax_unit("al_agi", period)
        return max_(0, misc_expense - misc_floor)
