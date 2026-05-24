from policyengine_us.model_api import *


class uncapped_roth_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped Roth 401(k) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("roth_401k_contributions_desired", period)
