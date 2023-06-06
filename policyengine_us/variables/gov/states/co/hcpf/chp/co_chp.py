from policyengine_us.model_api import *


class co_chp(Variable):
    value_type = float
    entity = Person
    label = "Child Health Plan Plus"
    definition_period = YEAR
    defined_for = "co_chp_eligible"

    def formula(person, period, parameters):
        return 0
