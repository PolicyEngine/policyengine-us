from policyengine_us.model_api import *


class co_chp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child Health Plan Plus eligibility"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        medicaid_eligible = person('is_medicaid_eligible', period)
        income_level = person('medicaid_income_level', period)
        in_income_range = income_level <= 2.6
        return ~medicaid_eligible & in_income_range
