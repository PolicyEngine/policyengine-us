from openfisca_us.model_api import *


class is_older_child_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Older children"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_D"

    def formula(person, period, parameters):
        age = person("age", period)
        ma = parameters(period).hhs.medicaid.eligibility.categories.older_child
        income = person("medicaid_income_level", period)
        is_older_child = ma.age_range.calc(age)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return is_older_child & (income < income_limit)
