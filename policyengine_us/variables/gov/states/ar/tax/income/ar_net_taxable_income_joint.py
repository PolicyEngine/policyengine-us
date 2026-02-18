from policyengine_us.model_api import *


class ar_net_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas net taxable income when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2024_AR1000F_and_AR1000NR_Instructions.pdf",
        "https://law.justia.com/codes/arkansas/title-26/subtitle-5/chapter-51/subchapter-5/section-26-51-501/",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        taxable_income = person("ar_taxable_income_joint", period)
        uses_low_income_tax_tables = person.tax_unit(
            "ar_uses_low_income_tax_tables", period
        )
        # When the low income table is used, the standard deduction
        # is built in, so use AGI instead of taxable income.
        agi = person("ar_agi_joint", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(agi)
        return where(
            uses_low_income_tax_tables,
            total_agi,
            taxable_income,
        )
