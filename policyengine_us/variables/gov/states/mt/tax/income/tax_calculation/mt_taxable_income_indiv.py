from policyengine_us.model_api import *


class mt_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16",
    )

    def formula(person, period, parameters):
        pre_dependent_exemption_income = person(
            "mt_pre_dependent_exemption_taxable_income_indiv", period
        )
        dependent_exemptions = add(
            person.tax_unit, period, ["mt_dependent_exemptions_person"]
        )
        # The dependent exemptions are allocated optimally between the head and spouse
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_income = person.tax_unit.sum(
            pre_dependent_exemption_income * head
        )
        spouse_income = person.tax_unit.sum(
            pre_dependent_exemption_income * spouse
        )
        # Calculate the difference between the head and spouse income
        income_difference = np.abs(head_income - spouse_income)
        # Cap the exemption amount initially at the difference between the head and spouse income
        exemptions_capped_at_income_difference = min_(
            income_difference, dependent_exemptions
        )
        head_income_exceeds_spouse_income = head_income > spouse_income
        # The capped exemptions are allocated to the spouse with the larger income
        spouse_with_larger_income = where(
            head_income_exceeds_spouse_income, head, spouse
        )
        exemptions_capped_at_income_difference_allocated_to_spouse_with_larger_income = (
            exemptions_capped_at_income_difference * spouse_with_larger_income
        )
        # The remaining exemption amount is halved and allocated between the head and spouse
        remaining_exemptions = (
            dependent_exemptions - exemptions_capped_at_income_difference
        )
        halved_remaining_exemptions = remaining_exemptions / 2
        return max_(
            pre_dependent_exemption_income
            - exemptions_capped_at_income_difference_allocated_to_spouse_with_larger_income
            - halved_remaining_exemptions,
            0,
        )
