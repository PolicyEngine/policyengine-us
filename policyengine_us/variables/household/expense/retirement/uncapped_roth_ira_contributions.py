from policyengine_us.model_api import *


class uncapped_roth_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped Roth IRA contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("roth_ira_contributions_desired", period)
