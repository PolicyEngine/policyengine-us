from openfisca_us.model_api import *


class is_older_child_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid older child financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).hhs.medicaid.eligibility.categories.older_child
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return income < income_limit
