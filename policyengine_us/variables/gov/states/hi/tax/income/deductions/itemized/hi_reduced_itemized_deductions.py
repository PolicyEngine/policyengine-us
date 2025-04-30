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
        total_deductions = tax_unit("hi_total_itemized_deductions", period)
        partial_deductions = add(
            tax_unit,
            period,
            [
                "hi_medical_expense_deduction",
                "investment_interest_expense",
                "hi_casualty_loss_deduction",
            ],
        )

        # eligible check 1: deduction_difference need to be greater than 0 to have reduced deduction
        partial_deductions_less_than_total = (
            partial_deductions < total_deductions
        )
        total_less_partial_ded_amount = total_deductions - partial_deductions
        # Take a percentage of the difference between the total and partial deductions
        # Hawaii applies federal limits which have been revoked in 2018
        p_2017 = parameters(
            f"2017-01-01"
        ).gov.irs.deductions.itemized.reduction
        total_less_partial_ded_percentage = (
            total_less_partial_ded_amount * p_2017.rate.base
        )
        # eligible check 2: actual AGI need to be smaller than AGI cap
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        # Hawaii applies an federal AGI limit as of 2009.
        p_hi = parameters(
            period
        ).gov.states.hi.tax.income.deductions.itemized.threshold
        agi_threshold = p_hi.reduction[filing_status]
        agi_over_threshold = agi_threshold < hi_agi
        # If the AGI is over a threshold, the AGI amount is reduced by the threshold and multiplied
        # by a rate
        reduced_agi = hi_agi - agi_threshold
        reduced_agi_percentage = reduced_agi * p_2017.rate.excess_agi

        smaller_reduced_ded = min_(
            total_less_partial_ded_percentage, reduced_agi_percentage
        )
        reduced_deductions = max_(0, total_deductions - smaller_reduced_ded)
        eligible = partial_deductions_less_than_total & agi_over_threshold
        return eligible * reduced_deductions
