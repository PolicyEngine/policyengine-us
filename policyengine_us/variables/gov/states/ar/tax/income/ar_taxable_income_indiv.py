from policyengine_us.model_api import *


class ar_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Arkansas taxable income when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        agi = person("ar_agi", period)
        deductions = person("ar_deduction_indiv", period)
        return max_(0, agi - deductions)
