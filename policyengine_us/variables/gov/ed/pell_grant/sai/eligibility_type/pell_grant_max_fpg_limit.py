from policyengine_us.model_api import *


class pell_grant_max_fpg_percent_limit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the maximum Pell Grant"

    def formula(person, period, parameters):
        return 0
