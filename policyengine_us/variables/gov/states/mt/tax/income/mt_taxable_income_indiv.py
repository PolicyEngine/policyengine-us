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

        standard_deduction = person("mt_standard_deduction_indiv", period)
        itemized_deductions = person("mt_itemized_deductions_indiv", period)
        # Tax units can claim the larger of the itemized or standard deductions
        deductions = max_(itemized_deductions, standard_deduction)
        exemptions = person("mt_exemptions_indiv", period)
        deductions_and_exemptions = deductions + exemptions
        # allocata the deduction and exemption amounts based on the difference between and spouse AGI
        head_agi = person("is_tax_unit_head", period) * mt_agi
        spouse_agi = person("is_tax_unit_spouse", period) * mt_agi
        head_over_spouse_agi = head_agi > spouse_agi
        difference = min_(abs(head_agi - spouse_agi), deductions_and_exemptions)
        halved_excess_deduction = max_(deductions_and_exemptions - difference, 0) / 2
        head_reduced_agi = head_agi - halved_excess_deduction
        spouse_reduced_agi = spouse_agi - halved_excess_deduction
        return where(head_over_spouse_agi, max_(head_reduced_agi - difference, 0), max_(spouse_reduced_agi - difference, 0))
