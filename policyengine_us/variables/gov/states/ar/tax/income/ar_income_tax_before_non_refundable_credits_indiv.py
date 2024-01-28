from policyengine_us.model_api import *


class ar_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas income tax before non refundable credits when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_Final_AR1000ES.pdf"
    defined_for = "ar_can_file_separate_on_same_return"

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_indiv", period)

        main_rate = rate.calc(taxable_income)
        # Assuming that the filer will pick the option which will reduce tax liability the most
        low_income_tax = person("ar_low_income_tax_indiv", period)
        return min_(main_rate, low_income_tax)
