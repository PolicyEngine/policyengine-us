from openfisca_us.model_api import *


class tax_unit_taxable_ira_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit taxable IRA income"
    unit = USD
    documentation = "Taxable IRA distributions for the tax unit."
    definition_period = YEAR

    formula = sum_among_non_dependents("taxable_ira_income")

tc_e01500 = taxcalc_read_only_variable("tc_e01500", tax_unit_taxable_ira_income)