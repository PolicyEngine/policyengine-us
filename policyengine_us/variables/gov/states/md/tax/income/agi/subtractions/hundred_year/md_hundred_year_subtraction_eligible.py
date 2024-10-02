from policyengine_us.model_api import *


class md_hundred_year_subtraction_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Maryland hundred year subtraction"
    definition_period = YEAR
    reference = "https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/"
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(
            period
        ).gov.states.md.tax.income.agi.subtractions.hundred_year
        return age >= p.age_threshold
