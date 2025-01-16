from policyengine_us.model_api import *


class hi_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii medical expense deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p_deductions = parameters(period).gov.irs.deductions

        # 1. medical_expense_deduction: worksheet A-1
        # use hi_agi instead of AGI
        medical_expense = add(
            tax_unit, period, ["medical_out_of_pocket_expenses"]
        )
        hi_agi = tax_unit("hi_agi", period)
        medical_capped_amount = max_(
            0, p_deductions.itemized.medical.floor * hi_agi
        )
        return max_(0, medical_expense - medical_capped_amount)
