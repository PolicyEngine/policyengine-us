from policyengine_us.model_api import *


class medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medical expense deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/213#a"
    unit = USD
    documentation = "Itemized medical expenses deducted from taxable income."

    def formula(tax_unit, period, parameters):
        expense = tax_unit("itemized_medical_expenses", period)
        p = parameters(period).gov.irs.deductions.itemized.medical
        medical_floor = p.floor * tax_unit("positive_agi", period)
        return max_(0, expense - medical_floor)
