from policyengine_us.model_api import *


class ms_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi taxable income when married couple file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        ms_taxable_income_indiv_head = add(tax_unit, period, ["ms_taxable_income_indiv_head"])

        ms_taxable_income_indiv_spouse = add(tax_unit, period, ["ms_taxable_income_indiv_spouse"])
        total_taxable_income = (
            ms_taxable_income_indiv_head + ms_taxable_income_indiv_spouse
        )
        #  negative amount will be no income tax liability
        head = person("is_tax_unit_head", period)
        return head * max_(total_taxable_income, 0)
