from policyengine_us.model_api import *


class ar_net_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas net taxable income when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2024_AR1000F_and_AR1000NR_Instructions.pdf"
    documentation = (
        "Net taxable income from AR1000F Line 28. When the low income "
        "tax table is used, this equals AGI (without deductions "
        "subtracted, since the standard deduction is built into the "
        "low income tax table). Otherwise, it equals AGI minus "
        "deductions."
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        agi = person("ar_agi_joint", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(agi)
        deductions = person("ar_deduction_joint", period)
        total_deductions = person.tax_unit.sum(deductions)
        taxable_income = max_(0, total_agi - total_deductions)
        uses_low_income_tax_tables = person.tax_unit(
            "ar_uses_low_income_tax_tables", period
        )
        return where(
            uses_low_income_tax_tables,
            total_agi,
            taxable_income,
        )
