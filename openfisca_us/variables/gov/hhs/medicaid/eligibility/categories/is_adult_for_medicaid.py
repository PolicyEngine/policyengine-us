from openfisca_us.model_api import *


class is_adult_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Working-age and childless adults"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII"
    )

    def formula(person, period, parameters):
        age = person("age", period)
        ma = parameters(period).hhs.medicaid.eligibility.categories.adult
        is_adult = ma.age_range.calc(age)
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return is_adult & (income < income_limit)
