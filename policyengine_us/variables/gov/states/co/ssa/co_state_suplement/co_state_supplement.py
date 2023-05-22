from policyengine_us.model_api import *


class co_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement"
    definition_period = YEAR
    defined_for = "co_state_supplement_eligible"

    def formula(person, period, parameters):
        income = person("ssi_countable_income", period)
        ssi = person("ssi", period)
        total_countable_income = ssi + income
        grant_standard = 1000
        return max_(0, grant_standard - total_countable_income)
