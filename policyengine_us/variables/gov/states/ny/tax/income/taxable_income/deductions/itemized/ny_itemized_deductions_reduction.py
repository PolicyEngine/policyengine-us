from policyengine_us.model_api import *


class ny_itemized_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY itemized deductions reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (f)&(g)
    defined_for = "ny_itemized_deductions_reduction_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.reduction
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)
        itemized_deduction = tax_unit("ny_itemized_deductions_max", period)
        charitable_deduction = tax_unit("charitable_deduction", period)
        # Income thresholds for itemized deductions reduction
        lower_income_threshold = p.income_threshold.lower[filing_status]
        addition_reduction_income_threshold = p.income_threshold.higher
        high_income_threshold = p.high_income_brackets.thresholds[1]
        higher_income_threshold = p.high_income_brackets.thresholds[2]

        lower_income_condition = agi <= addition_reduction_income_threshold
        lower_income_excess_amount = agi - lower_income_threshold
        lower_income_base_amount = min_(
            p.amount.numerator, lower_income_excess_amount
        )
        lower_income_multiplier = (
            lower_income_base_amount / p.amount.denominator
        )
        lower_income_reduction_amount = (
            p.rate.lower * itemized_deduction * lower_income_multiplier
        )
        addition_reduction_condition = (
            agi > addition_reduction_income_threshold
        ) & (agi <= high_income_threshold)
        addition_reduction_excess_amount = max_(
            agi - addition_reduction_condition, 0
        )
        addition_reduction_base_amount = min_(
            p.amount.numerator, addition_reduction_excess_amount
        )
        addition_reduction_multiplier = (
            addition_reduction_base_amount / p.amount.denominator
        )
        addition_reduction_amount = (
            p.rate.higher * itemized_deduction * addition_reduction_multiplier
        )
        high_income_condition = (agi > high_income_threshold) & (
            agi <= higher_income_threshold
        )
        # For filers with NY AGI higher than $1,000,000, only fraction of their
        # charitable deduction can be applied to itemized deduction
        high_income_rate = p.high_income_brackets.rates[1]
        high_income_reduction = (
            itemized_deduction - high_income_rate * charitable_deduction
        )
        higher_income_condition = agi > higher_income_threshold
        higher_income_rate = p.high_income_brackets.rates[2]
        higher_income_reduction = (
            itemized_deduction - higher_income_rate * charitable_deduction
        )

        return select(
            [
                lower_income_condition,
                addition_reduction_condition,
                high_income_condition,
                higher_income_condition,
            ],
            [
                lower_income_reduction_amount,
                lower_income_reduction_amount + addition_reduction_amount,
                high_income_reduction,
                higher_income_reduction,
            ],
            default=0,
        )
