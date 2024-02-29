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
        head_agi = tax_unit.sum(mt_agi * head)
        spouse_agi = tax_unit.sum(mt_agi * spouse)
        head_exceeds_spouse_agi = head_agi > spouse_agi
        # Determine the difference between the two AGIs and cap the deductions at that amount.
        # The head only gets this portion if they have larger AGI.
        agi_difference = np.abs(head_agi - spouse_agi)
        deductions_capped_at_agi_difference = min_(
            agi_difference, total_deductions_exemptions
        )
        equalizing_amount = (
            deductions_capped_at_agi_difference * head_exceeds_spouse_agi
        )
        # Halve the remaining deductions amount
        # Both head and spouse receive this amount.
        remaining_deductions_exemptions = (
            total_deductions_exemptions - deductions_capped_at_agi_difference
        )
        halved_remaining_deductions = remaining_deductions_exemptions / 2
        return halved_remaining_deductions + equalizing_amount
