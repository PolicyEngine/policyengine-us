from policyengine_us.model_api import *


class al_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2021/title-40/chapter-18/article-1/section-40-18-15/"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        expense = add(tax_unit, period, ["medical_expense"])
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        medical_floor = p.medical_expense * tax_unit("positive_agi", period)
        return max_(0, expense - medical_floor)
