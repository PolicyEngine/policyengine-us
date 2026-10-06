from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ar.tax.income.ar_income_tax_helpers import (
    ar_main_income_tax,
)


class ar_uses_low_income_tax_tables(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the filer uses the low income tax tables"
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_and_AR1000NR_Instructions.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2024_AR1000F_and_AR1000NR_Instructions.pdf",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.rates.main
        person = tax_unit.members
        taxable_income = person("ar_taxable_income_joint", period)
        total_main_rate_person = max_(ar_main_income_tax(taxable_income, p), 0)
        total_main_rate = tax_unit.sum(total_main_rate_person)
        low_income_tax = add(tax_unit, period, ["ar_low_income_tax_joint"])
        return total_main_rate > low_income_tax
