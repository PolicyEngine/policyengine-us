from policyengine_us.model_api import *


class ms_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Share of allocable Mississippi joint deductions and exemptions"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-17/",  # MS Code 27-7-17: deductions may be divided in any manner
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-21/",  # MS Code 27-7-21: exemptions may be divided in any manner
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        tax = parameters(period).gov.states.ms.tax.income
        rate = tax.rate

        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        agi = person("ms_agi", period)

        head_agi = tax_unit.sum(agi * is_head)
        spouse_agi = tax_unit.sum(agi * is_spouse)

        filing_status = tax_unit("filing_status", period)
        standard_deduction = tax.deductions.standard.amount[filing_status]
        itemized_deductions = tax_unit("ms_itemized_deductions_unit", period)
        total_exemptions = tax_unit("ms_total_exemptions", period)
        total_allocable_deductions = (
            max_(standard_deduction, itemized_deductions) + total_exemptions
        )

        best_head_allocation = allocate_joint_amount_to_minimize_combined_tax(
            rate, head_agi, spouse_agi, total_allocable_deductions
        )

        head_fraction = where(
            total_allocable_deductions > 0,
            best_head_allocation / total_allocable_deductions,
            is_head,
        )

        return where(is_head, head_fraction, where(is_spouse, 1 - head_fraction, 0))
