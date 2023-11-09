from policyengine_us.model_api import *


class md_hundred_year_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Maryland hundred year subtraction per person"
    unit = USD
    definition_period = YEAR
    reference = "https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/"
    defined_for = "md_hundred_year_subtraction_eligible"

    def formula(person, period, parameters):
        return parameters(
            period
        ).gov.states.md.tax.income.agi.subtractions.hundred_year.amount
