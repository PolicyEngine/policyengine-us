from policyengine_us.model_api import *


class ar_net_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas net taxable income when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    documentation = "This variable accounts for the usage of the low income tax tables which prompts the exclusion of the state standard or itemized deductions and used in the calculation of the inflationary relief tax credit and additional tax credit for qualified individuals."
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        agi = person("ar_agi_joint", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(agi)
        deductions = person("ar_deduction_joint", period)
        total_deductions = person.tax_unit.sum(deductions)
        taxable_income_reduced_by_deductions = max_(
            0, total_agi - total_deductions
        )
        uses_low_income_tax_tables = person.tax_unit(
            "ar_uses_low_income_tax_tables", period
        )
        return where(
            uses_low_income_tax_tables,
            total_agi,
            taxable_income_reduced_by_deductions,
        )
