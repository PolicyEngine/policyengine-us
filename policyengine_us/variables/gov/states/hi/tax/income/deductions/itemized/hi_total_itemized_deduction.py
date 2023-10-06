from policyengine_us.model_api import *


class hi_total_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii total itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized

        # we need adjustments for medical_expense_deduction, interest_deduction and casualty_loss_deduction
        hi_itemized_deductions = [
            "charitable_deduction",
            "hi_medical_expense_deduction",
            "hi_interest_deduction",
            "hi_casualty_loss_deduction",
        ]

        return add(tax_unit, period, hi_itemized_deductions)
