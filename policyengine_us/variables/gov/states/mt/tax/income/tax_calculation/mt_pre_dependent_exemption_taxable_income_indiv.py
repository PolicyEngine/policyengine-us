from policyengine_us.model_api import *


class mt_pre_dependent_exemption_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income before the dependent exemption when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=16",
    )

    def formula(person, period, parameters):
        mt_agi = person("mt_agi_indiv", period)
        exemptions = person("mt_personal_exemptions_indiv", period)
        deductions = person("mt_deductions_indiv", period)
        return max_(mt_agi - exemptions - deductions, 0)
