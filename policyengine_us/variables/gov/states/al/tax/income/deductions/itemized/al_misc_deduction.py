from policyengine_us.model_api import *


class al_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama miscellaneous itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/",  # Code of Alabama Section 40-18-15(a)(23)
        # Act 2026-604, Section 1. PDF pages 7-8
        "https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/HB527-enr.pdf#page=7",
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1",  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1",  # 2021 Schedule A (Form 1040)
        # 2024 Form 40 instructions, Schedule A lines 20 to 24. PDF pages 20-21
        "https://www.revenue.alabama.gov/wp-content/uploads/2025/01/24f40bk.pdf#page=20",
        # 2025 Form 40 instructions, Schedule A lines 20 to 24.
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=21",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        # Ala. Code 40-18-15(a)(23) allows the subdivision (1) unreimbursed
        # employee business expenses and the subdivision (14) deduction only
        # above 2% of Alabama AGI. Alabama applies this floor to the expenses
        # themselves, in every year, so the formula does not start from the
        # federal misc_deduction: that is already net of the federal 2% floor
        # and is zero once 26 U.S.C. 67(g) suspends it from 2018. Alabama keeps
        # its own list of expenses so that federal categories added later do
        # not flow in without a reading of the Alabama statute. Like al_agi,
        # it sums the head's and spouse's expenses only: a tax unit
        # dependent's expenses belong on the dependent's own Alabama return.
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        expenses = tax_unit_non_dep_add(tax_unit, period, p.misc_sources)
        misc_floor = p.work_related_expense_rate * tax_unit("al_agi", period)
        return max_(0, expenses - misc_floor)
