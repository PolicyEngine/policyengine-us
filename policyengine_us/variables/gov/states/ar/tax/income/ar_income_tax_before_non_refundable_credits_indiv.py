from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ar.tax.income.ar_income_tax_helpers import (
    ar_main_income_tax,
)


class ar_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas income tax before non refundable credits when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_indiv", period)
        return max_(ar_main_income_tax(taxable_income, p), 0)
