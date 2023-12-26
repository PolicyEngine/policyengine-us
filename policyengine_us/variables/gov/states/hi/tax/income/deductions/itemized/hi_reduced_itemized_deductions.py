from policyengine_us.model_api import *


class hi_reduced_itemized_deductions(Variable):
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

    # If the state AGI of the filer exceeds a certain amount, only partial itemized deductions 
    # can be deducted.
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_irs = parameters(period).gov.irs.deductions.itemized.reduced_rate

        total_deductions = tax_unit("hi_total_itemized_deductions", period)
        partial_deductions = add(tax_unit, period, [
            "hi_medical_expense_deduction",
            "investment_interest_expense",
            "hi_casualty_loss_deduction",
        ])

        # eligible check 1: deduction_difference need to be greater than 0 to have reduced deduction
        partial_deductions_less_than_total = partial_deductions < total_deductions
        deduction_difference = total_deductions - partial_deductions
        reduced_difference = deduction_difference * p_irs.amount
        # eligible check 2: actual AGI need to be smaller than AGI cap
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_threshold = p.cap.agi[filing_status]
        agi__over_threshold = agi_threshold < hi_agi
        agi_cap_difference = hi_agi - agi_threshold
        reduced_agi_difference = agi_cap_difference * p_irs.excess_agi

        smaller_reduced = min_(reduced_difference, reduced_agi_difference)
        reduced_deductions = max_(0, total_deductions - smaller_reduced)

        return where(
            (partial_deductions_less_than_total & agi__over_threshold),
            reduced_deductions,
            0,
        )
