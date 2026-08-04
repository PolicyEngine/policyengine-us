from policyengine_us.model_api import *


class is_parent_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid parent financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        income = person("medicaid_income_level", period)
        income_limit = person("medicaid_parent_income_limit", period)
        return income <= income_limit
