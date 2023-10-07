from policyengine_us.model_api import *


class al_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama Work Related Expense"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
    reference = (
        "https://law.justia.com/codes/alabama/2021/title-40/chapter-18/article-1/section-40-18-15/"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        misc_expense = tax_unit("misc_deduction", period)
        return misc_expense * p.misc_deduction
