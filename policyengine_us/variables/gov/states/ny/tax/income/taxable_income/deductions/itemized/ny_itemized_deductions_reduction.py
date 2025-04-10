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
        additional_reduction_income_threshold = p.income_threshold.higher
        high_income_threshold = p.high_income_brackets.thresholds[1]
        higher_income_threshold = p.high_income_brackets.thresholds[2]

        # Worksheet 3: 100,000(amount based on filling status) < AGI <= 475,000
        # first reduction amount = 0.25* itemized_deduction* min_(agi - 100,000, 50,000)/ $50,000
        lower_income_condition = agi <= additional_reduction_income_threshold
        lower_income_excess_amount = max_(agi - lower_income_threshold, 0)
        lower_income_base_amount = min_(
            p.amount.numerator, lower_income_excess_amount
        )
        lower_income_multiplier = (
            lower_income_base_amount / p.amount.denominator
        )
        lower_income_reduction_amount = (
            p.rate.lower * itemized_deduction * lower_income_multiplier
        )
        # This part aligns with leagl code description
        # Worksheet 4: 475,000 < AGI <= 1,000,000
        # combined worksheet 4 and the quote
        # "more than $525,000 but not more than $1,000,000, enter 50% (.50) of itemized deduction"
        additional_reduction_condition = (
            agi > additional_reduction_income_threshold
        ) & (agi <= high_income_threshold)
        additional_reduction_excess_amount = max_(
            agi - additional_reduction_income_threshold, 0
        )
        addition_reduction_base_amount = min_(
            p.amount.numerator, additional_reduction_excess_amount
        )
        additional_reduction_multiplier = (
            addition_reduction_base_amount / p.amount.denominator
        )
        additional_reduction_amount = (
            p.rate.higher
            * itemized_deduction
            * additional_reduction_multiplier
        )
        # For filers with NY AGI higher than $1,000,000, only fraction of their
        # charitable deduction can be applied to itemized deduction
        # Worksheet 5: 1,000,000 < AGI <= 10,000,000
        # reduction amount = itemized_deduction - 0.5 * charitable_deduction
        high_income_condition = (agi > high_income_threshold) & (
            agi <= higher_income_threshold
        )
        high_income_rate = p.high_income_brackets.rates[1]
        high_income_reduction = (
            itemized_deduction - high_income_rate * charitable_deduction
        )
        # Worksheet 6: AGI > 10,000,000
        # reduction amount = itemized_deduction - 0.25 * charitable_deduction
        higher_income_condition = agi > higher_income_threshold
        higher_income_rate = p.high_income_brackets.rates[2]
        higher_income_reduction = (
            itemized_deduction - higher_income_rate * charitable_deduction
        )

        return select(
            [
                lower_income_condition,
                additional_reduction_condition,
                high_income_condition,
                higher_income_condition,
            ],
            [
                lower_income_reduction_amount,
                lower_income_reduction_amount + additional_reduction_amount,
                high_income_reduction,
                higher_income_reduction,
            ],
            default=0,
        )
