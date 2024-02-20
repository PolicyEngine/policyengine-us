from policyengine_us.model_api import *


class mt_head_deductions_exemptions_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "The total amount of Montana deductions and exemptions when married filing separately attributed to the head of the tax unit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        mt_agi = person("mt_agi", period)
        total_deductions_exemptions = tax_unit(
            "mt_tax_unit_deductions_exemptions_indiv", period
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_agi = mt_agi * head
        spouse_agi = mt_agi * spouse
        spouse_agi_attributed_to_head = tax_unit.sum(spouse_agi) * head
        head_over_spouse_agi = head_agi > spouse_agi_attributed_to_head
        # Determine the difference between the two AGIs and cap the deductions at that amount
        difference = tax_unit.sum(
            np.abs(head_agi - spouse_agi_attributed_to_head)
        )
        deductions_capped_at_agi_difference = min_(
            difference, total_deductions_exemptions
        )
        # Halve the remaining deductions amount
        halved_capped_deductions = (
            total_deductions_exemptions - deductions_capped_at_agi_difference
        ) * 0.5
        halved_deductions_allocated_to_head_or_spouse = (
            halved_capped_deductions * head
        )
        difference_applied_to_agi = (
            deductions_capped_at_agi_difference
            * where(head_over_spouse_agi, 1, 0)
        )
        return tax_unit.sum(
            difference_applied_to_agi
            + halved_deductions_allocated_to_head_or_spouse
        )
