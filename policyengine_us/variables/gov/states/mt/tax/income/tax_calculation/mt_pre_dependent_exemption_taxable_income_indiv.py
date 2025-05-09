from policyengine_us.model_api import *


class mt_pre_dependent_exemption_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income before the dependent exemption when married couples are filing separately"
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
        return max_(mt_agi - exemptions - deductions, 0)
