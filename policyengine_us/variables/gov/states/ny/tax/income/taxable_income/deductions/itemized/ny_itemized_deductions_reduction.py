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
        # Income threshold itemized deductions reduction
        first_reduction_threshold = p.amount.first_reduction[
            filing_status
        ]  # 100_000
        second_reduction_threshold = p.amount.second_reduction  # 475_000
        # Income threshold where only charitable deduction applies
        high_income_threshold = p.amount.high_income
        higher_income_threshold = p.amount.higher_income

        first_reduction_condition = agi <= second_reduction_threshold
        first_reduction_excess_amount = agi - first_reduction_threshold
        first_reduction_base_amount = min_(
            p.amount.numerator, first_reduction_excess_amount
        )
        first_reduction_multiplier = (
            first_reduction_base_amount / p.amount.denominator
        )
        first_reduction = (
            p.rate.first_reduction
            * itemized_deduction
            * first_reduction_multiplier
        )
        second_reduction_condition = (
            second_reduction_threshold < agi <= high_income_threshold
        )
        second_reduction_excess_amount = max_(
            agi - second_reduction_threshold, 0
        )
        second_reduction_base_amount = min_(
            p.amount.numerator, second_reduction_excess_amount
        )
        second_reduction_multiplier = (
            second_reduction_base_amount / p.amount.denominator
        )
        second_reduction = (
            p.rate.second_reduction
            * itemized_deduction
            * second_reduction_multiplier
        )
        high_income_condition = (
            high_income_threshold < agi <= higher_income_threshold
        )
        high_income_reduction = (
            itemized_deduction - p.rate.high_income * charitable_deduction
        )
        higher_income_condition = agi > higher_income_threshold
        higher_income_reduction = (
            itemized_deduction - p.rate.higher_income * charitable_deduction
        )

        return select(
            [
                first_reduction_condition,
                second_reduction_condition,
                high_income_condition,
                higher_income_condition,
            ],
            [
                first_reduction,
                first_reduction + second_reduction,
                high_income_reduction,
                higher_income_reduction,
            ],
            default=0,
        )
