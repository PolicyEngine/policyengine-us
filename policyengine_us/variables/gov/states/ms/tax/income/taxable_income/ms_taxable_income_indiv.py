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
        
        # taxable_income_spouse = person("ms_taxable_income_indiv_spouse", period)
        # taxable_income_head = person("ms_taxable_income_indiv_head", period)
        # if_combined_taxable_income = (taxable_income_spouse < 0) | (taxable_income_head < 0)

        # # Both head and spouse have positive taxable income
        # taxable_income_uncombined = [taxable_income_head[i] + taxable_income_spouse[i] for i in range(len(taxable_income_head))]

        # # Only one of the head or spouse have postive taxable income
        # tax_unit = person.tax_unit
        # ms_taxable_income_indiv_head = add(tax_unit, period, ["ms_taxable_income_indiv_head"])
        # ms_taxable_income_indiv_spouse = add(tax_unit, period, ["ms_taxable_income_indiv_spouse"])
        # total_taxable_income = (
        #     ms_taxable_income_indiv_head + ms_taxable_income_indiv_spouse
        # )
        # #  negative amount will be no income tax liability
        # head = person("is_tax_unit_head", period)
        # taxable_income_combined = head * max_(total_taxable_income, 0)

        # return where(if_combined_taxable_income, taxable_income_combined, taxable_income_uncombined)