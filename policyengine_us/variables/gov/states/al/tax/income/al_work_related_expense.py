from policyengine_us.model_api import *


class al_work_related_expense(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama Work Related Expense"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/02/22f40.pdf"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        work_related = tax_unit("work_related_expense", period)
        deduction_value = p.work_related_expense * work_related
        return deduction_value