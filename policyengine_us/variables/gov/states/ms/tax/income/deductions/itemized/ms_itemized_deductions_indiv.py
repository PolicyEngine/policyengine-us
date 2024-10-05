from policyengine_us.model_api import *


class ms_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi itemized deductions for individual couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7"
        "https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU"
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        pre_deductions_taxable_income = person(
            "ms_pre_deductions_taxable_income_indiv", period
        )
        unit_deds = person.tax_unit("ms_itemized_deductions_unit", period)
        # The itemized deductions are allocated optimally between the head and spouse
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_income = person.tax_unit.sum(pre_deductions_taxable_income * head)
        spouse_income = person.tax_unit.sum(
            pre_deductions_taxable_income * spouse
        )
        # Calculate the difference between the head and spouse income
        income_difference = np.abs(head_income - spouse_income)
        # Cap the deduction amount initially at the difference between the head and spouse income
        deductions_capped_at_income_difference = min_(
            income_difference, unit_deds
        )
        head_income_exceeds_spouse_income = head_income > spouse_income

        # The capped deductions are allocated to the spouse with the larger income
        spouse_with_larger_income = where(
            head_income_exceeds_spouse_income, head, spouse
        )

        deductions_capped_at_income_difference_allocated_to_spouse_with_larger_income = (
            deductions_capped_at_income_difference * spouse_with_larger_income
        )

        # The remaining deductions are halved and allocated between the head and spouse
        remaining_deductions = (
            unit_deds - deductions_capped_at_income_difference
        )
        head_or_spouse = head | spouse
        halved_remaining_deductions = (
            remaining_deductions / 2
        ) * head_or_spouse
        return (
            deductions_capped_at_income_difference_allocated_to_spouse_with_larger_income
            + halved_remaining_deductions
        )
