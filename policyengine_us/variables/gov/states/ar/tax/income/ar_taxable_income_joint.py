from policyengine_us.model_api import *


class ar_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable income when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        agi = person("ar_agi_joint", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(agi)
        deductions = person("ar_deduction_joint", period)
        total_deductions = person.tax_unit.sum(deductions)
        return max_(0, total_agi - total_deductions)
