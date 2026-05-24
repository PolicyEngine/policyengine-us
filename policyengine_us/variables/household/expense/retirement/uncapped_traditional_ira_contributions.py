from policyengine_us.model_api import *


class uncapped_traditional_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped traditional IRA contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("traditional_ira_contributions_desired", period)
