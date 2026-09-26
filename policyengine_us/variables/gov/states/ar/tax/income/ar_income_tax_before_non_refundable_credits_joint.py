from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ar.tax.income.ar_income_tax_helpers import (
    ar_main_income_tax,
)


class ar_income_tax_before_non_refundable_credits_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Arkansas income tax before non refundable credits when married filing jointly"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/wp-content/uploads/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_joint", period)
        total_main_rate = max_(ar_main_income_tax(taxable_income, p), 0)
        low_income_tax = person("ar_low_income_tax_joint", period)
        return min_(total_main_rate, low_income_tax)
