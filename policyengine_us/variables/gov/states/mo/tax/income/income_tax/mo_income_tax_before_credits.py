from policyengine_us.model_api import *


class mo_income_tax_before_credits(Variable):
    value_type = float
    entity = Person
    label = "Missouri income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf",
        "https://www.revisor.mo.gov/main/OneChapter.aspx?chapter=143",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        taxable_income = person("mo_taxable_income", period)
        rates = parameters(period).gov.states.mo.tax.income.rates
        return rates.calc(taxable_income)
