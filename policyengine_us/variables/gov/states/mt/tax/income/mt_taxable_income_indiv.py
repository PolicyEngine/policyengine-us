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
        return max_(0, mt_agi - deductions - exemptions)
