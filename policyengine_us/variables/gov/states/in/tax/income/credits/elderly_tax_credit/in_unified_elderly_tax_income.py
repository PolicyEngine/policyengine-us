from policyengine_us.model_api import *


class in_unified_elderly_tax_income(Variable):
    value_type = float
    entity = Person
    label = "Indiana unified elderly tax credit income"
    unit = USD
    definition_period = YEAR
    documention = "Income that is utilized for the elderly credit calculation"
    reference = "https://forms.in.gov/Download.aspx?id=15394 "
    defined_for = StateCode.IN

    def formula(person, period, parameters):
        employment = person("employment_income", period)
        self_employment = person("self_employment_income", period)
        interest = person("interest_income", period)
        dividend = person("dividend_income", period)
        rental_income = person("rental_income", period)
        unemployment = person("unemployment_compensation", period)
        pensions = person("pension_income", period)
        return (
            employment
            + self_employment
            + interest
            + dividend
            + rental_income
            + unemployment
            + pensions
        )
