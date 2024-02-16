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
        mt_agi = person("mt_agi", period)
        standard_deduction = add(
            person.tax_unit, period, ["mt_standard_deduction_indiv"]
        )
        itemized_deductions = add(
            person.tax_unit, period, ["mt_itemized_deductions_indiv"]
        )
        # Tax units can claim the larger of the itemized or standard deductions
        itemizes = person.tax_unit("mt_tax_unit_itemizes", period)
        deductions = where(itemizes, itemized_deductions, standard_deduction)
        exemptions = add(person.tax_unit, period, ["mt_exemptions_indiv"])
        deductions_and_exemptions = deductions + exemptions
        # Allocate the exemptions and deductions based on the following process:
        # 1. Determine whether the head or spouse AGI is larger
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_agi = mt_agi * head
        spouse_agi = mt_agi * spouse
        spouse_agi_attributed_to_head = person.tax_unit.sum(spouse_agi) * head
        head_over_spouse_agi = head_agi > spouse_agi_attributed_to_head
        # 2. Determine the difference between the two AGIs and cap the deductions at that amount
        difference = person.tax_unit.sum(
            abs(head_agi - spouse_agi_attributed_to_head)
        )
        deductions_capped_at_agi_difference = min_(
            difference, deductions_and_exemptions
        )
        # 3. Halve the remaining deductions amount
        halved_capped_deductions = (
            deductions_and_exemptions - deductions_capped_at_agi_difference
        ) * 0.5
        halved_deductions_allocated_to_head_or_spouse = (
            halved_capped_deductions * (head | spouse)
        )
        # 4. Allocate the difference to the higher AGI and the halved deductions to each head and spouse
        difference_applied_to_larger_agi = (
            deductions_capped_at_agi_difference
            * where(head_over_spouse_agi, head, spouse)
        )
        reduced_agi = (
            mt_agi
            - difference_applied_to_larger_agi
            - halved_deductions_allocated_to_head_or_spouse
        )
        return max_(reduced_agi, 0)
