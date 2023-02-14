from policyengine_us.model_api import *


class mo_income_tax_exempt(Variable):
    value_type = float
    entity = Person
    label = "Missouri income tax exempt"
    unit = USD
    definition_period = YEAR
    reference = "https://revisor.mo.gov/main/OneSection.aspx?section=143.021"
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        taxable_income = person("mo_taxable_income", period)
        p = parameters(period).gov.states.mo.tax.income
        return taxable_income <= p.minimum_taxable_income
