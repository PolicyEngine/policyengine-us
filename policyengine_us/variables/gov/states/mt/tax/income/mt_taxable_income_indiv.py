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
        exemptions = person("mt_personal_exemptions_indiv", period)
        deductions = person("mt_deductions_indiv", period)
        reduced_agi = max_(mt_agi - exemptions - deductions, 0)
        dependent_exemptions = add(
            person.tax_unit, period, ["mt_dependent_exemptions_person"]
        )
        head = person("is_tax_unit_head", period)
        head_deductions = person.tax_unit(
            "mt_head_dependent_exemptions_indiv", period
        )
        spouse_deductions = dependent_exemptions - head_deductions
        capped_head_agi = max_(reduced_agi - head_deductions, 0)
        capped_spouse_agi = max_(reduced_agi - spouse_deductions, 0)
        return where(head, capped_head_agi, capped_spouse_agi)
