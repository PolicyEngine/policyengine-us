from policyengine_us.model_api import *


class uncapped_traditional_403b_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped traditional 403(b) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("traditional_403b_contributions_desired", period)
