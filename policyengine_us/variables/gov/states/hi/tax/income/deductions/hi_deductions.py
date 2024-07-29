from policyengine_us.model_api import *


class hi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"  # Itemized Deduction
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"  # Standard Deduction
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized

        standard_deduction = tax_unit("hi_standard_deduction", period)
        total_itemized_deduction = tax_unit("hi_itemized_deductions", period)
        tax_unit_earned_income = tax_unit("tax_unit_earned_income", period)
        filing_status = tax_unit("filing_status", period)

        # check itemized deduction eligibility
        filing_status_eligible = (
            total_itemized_deduction > p.threshold.deductions[filing_status]
        )
        is_dependent_on_another_return = tax_unit(
            "head_is_dependent_elsewhere", period
        )
        standard_cap = min_(tax_unit_earned_income, standard_deduction)
        dependent_floor = max_(p.threshold.dependent, standard_cap)
        dependent_eligible = is_dependent_on_another_return & (
            total_itemized_deduction > dependent_floor
        )
        itemized_deductions_eligible = (
            filing_status_eligible | dependent_eligible
        )
        itemized_deduction = where(
            itemized_deductions_eligible, total_itemized_deduction, 0
        )
        return max_(itemized_deduction, standard_deduction)
