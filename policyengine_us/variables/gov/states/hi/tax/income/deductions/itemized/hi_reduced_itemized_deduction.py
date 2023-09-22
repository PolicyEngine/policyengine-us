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
        p_deductions = parameters(period).gov.irs.deductions

        total_deductions = tax_unit("hi_total_itemized_deduction", period)

        medical_expense = add(tax_unit, period, ["medical_expense"])
        hi_agi = tax_unit("hi_agi", period)
        medical_agi_amount = max_(
            0, p_deductions.itemized.medical.floor * hi_agi
        )
        hi_medical_expense_deduction = max_(
            0, medical_expense - medical_agi_amount
        )
        investment_interest = add(tax_unit, period, ["investment_interest"])
        casualty_loss = add(tax_unit, period, ["casualty_loss"])
        casualty_agi_amount = max_(
            0, p_deductions.itemized.casualty.floor * hi_agi
        )
        hi_casualty_loss_deduction = max(
            0, casualty_loss - casualty_agi_amount
        )
        partial_total_deductions = (
            hi_medical_expense_deduction
            + investment_interest
            + hi_casualty_loss_deduction
        )

        # eligible check 1: deduction_difference need to be greater than 0 to have reduced deduction
        difference_eligible = partial_total_deductions < total_deductions
        deduction_difference = total_deductions - partial_total_deductions
        reduced_difference = deduction_difference * p.reduced_rate
        # eligible check 2: actual agi need to be smaller than agi cap
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_cap = p.agi_cap[filing_status]
        agi_eligible = agi_cap < hi_agi
        agi_cap_difference = hi_agi - agi_cap
        reduced_agi_difference = agi_cap_difference * p.reduced_agi_rate

        smaller_reduced = min_(reduced_difference, reduced_agi_difference)
        reduced_deductions = total_deductions - smaller_reduced

        return where(
            (difference_eligible & agi_eligible),
            reduced_deductions,
            total_deductions,
        )
