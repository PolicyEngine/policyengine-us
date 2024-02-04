from policyengine_us.model_api import *


class mt_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16",
    )

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        head_agi = is_head * person.tax_unit.sum("mt_agi", period)
        standard_deduction = person("mt_standard_deduction_joint", period)
        itemized_deductions = person("mt_itemized_deductions_joint", period)
        # Tax units can claim the larger of the itemized or standard deductions
        deductions = max_(itemized_deductions, standard_deduction)
        total_deductions = add(person.tax_unit, period, deductions)
        exemptions = add(person.tax_unit, period, "mt_exemptions_joint")
        return max_(0, head_agi - total_deductions - exemptions)\
