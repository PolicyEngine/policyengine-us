from openfisca_us.model_api import *


class is_infant_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Is an infant for Medicaid"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_B"

    def formula(person, period, parameters):
        age = person("age", period)
        ma = parameters(period).hhs.medicaid.eligibility.categories.infant
        income = person("medicaid_income_level", period)
        is_infant = ma.age_range.calc(age)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return is_infant & (income < income_limit)
