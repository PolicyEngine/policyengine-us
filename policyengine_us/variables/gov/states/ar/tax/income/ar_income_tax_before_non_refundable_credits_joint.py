from policyengine_us.model_api import *


class ar_income_tax_before_non_refundable_credits_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas income tax before non refundable credits when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_Final_AR1000ES.pdf"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_joint", period)

        main_rate = rate.calc(taxable_income)

        low_income_tax = person("ar_low_income_tax_indiv", period)
        return min_(main_rate, low_income_tax)
