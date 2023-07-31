from policyengine_us.model_api import *

# import numpy as np


class ar_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_Final_AR1000ES.pdf"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = tax_unit("ar_taxable_income", period)

        return rate.calc(taxable_income)
