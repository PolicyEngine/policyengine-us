from policyengine_us.model_api import *


class hi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15\n"  # Itemized Deduction
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"  # Standard Deduction
    )
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=11",
        # PDF pages 15, 20
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=15",
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
        # HRS 235-2.4(a)(3) applies IRC 63(c)(5): the standard deduction of a
        # filer who can be claimed as a dependent is the greater of $500 or
        # earned income, up to the regular amount. As federally, a joint
        # return is limited when either spouse can be claimed.
        is_dependent_on_another_return = tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        # Worksheet earned income: wages and self-employment income minus the
        # deductible part of self-employment tax (Schedule 1, line 15).
        worksheet_earned_income = max_(
            tax_unit_earned_income - tax_unit("self_employment_tax_ald", period), 0
        )
        dependent_standard_deduction = min_(
            max_(p.threshold.dependent, worksheet_earned_income), standard_deduction
        )
        applicable_standard_deduction = where(
            is_dependent_on_another_return,
            dependent_standard_deduction,
            standard_deduction,
        )
        dependent_eligible = is_dependent_on_another_return & (
            total_itemized_deduction > dependent_standard_deduction
        )
        itemized_deductions_eligible = filing_status_eligible | dependent_eligible
        itemized_deduction = where(
            itemized_deductions_eligible, total_itemized_deduction, 0
        )
        return max_(itemized_deduction, applicable_standard_deduction)
