from policyengine_us.model_api import *


class hi_reduced_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii reduced itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_irs = parameters(period).gov.irs.deductions.itemized.reduced_rate

        total_deductions = tax_unit("hi_total_itemized_deduction", period)
        partial_itemized_deductions = [
            "hi_medical_expense_deduction",
            "investment_income_form_4952",
            "hi_casualty_loss_deduction",
        ]
        partial_deductions = add(tax_unit, period, partial_itemized_deductions)

        # eligible check 1: deduction_difference need to be greater than 0 to have reduced deduction
        difference_eligible = partial_deductions < total_deductions
        deduction_difference = total_deductions - partial_deductions
        reduced_difference = deduction_difference * p_irs.amount
        # eligible check 2: actual AGI need to be smaller than AGI cap
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_cap = p.cap.agi[filing_status]
        agi_eligible = agi_cap < hi_agi
        agi_cap_difference = hi_agi - agi_cap
        reduced_agi_difference = agi_cap_difference * p_irs.excess_agi

        smaller_reduced = min_(reduced_difference, reduced_agi_difference)
        reduced_deductions = max_(0, total_deductions - smaller_reduced)

        return where(
            (difference_eligible & agi_eligible),
            reduced_deductions,
            total_deductions,
        )
