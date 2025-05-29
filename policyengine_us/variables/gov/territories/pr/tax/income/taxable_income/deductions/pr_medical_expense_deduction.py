from policyengine_us.model_api import *


class pr_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=5"
    defined_for = StateCode.PR
    
    def formula(tax_unit, period, parameters):
        # line 1 - column A
        expense = add(tax_unit, period, ["medical_out_of_pocket_expenses"])
        p = parameters(period).gov.territories.pr.tax.income.taxable_income.deductions.medical
        # line 2
        medical_floor = p.floor * tax_unit("pr_agi", period)
        # line 3
        return max_(0, expense - medical_floor)