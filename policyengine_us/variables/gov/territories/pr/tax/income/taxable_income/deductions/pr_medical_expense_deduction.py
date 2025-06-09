from policyengine_us.model_api import *


class pr_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (4)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        expense = add(tax_unit, period, ["medical_out_of_pocket_expenses"])
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.medical
        medical_floor = p.floor * tax_unit("pr_agi", period)
        return max_(0, expense - medical_floor)
