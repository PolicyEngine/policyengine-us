from policyengine_us.model_api import *


class uncapped_traditional_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped traditional 401(k) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        desired = person("traditional_401k_contributions_desired", period)
        legacy_desired = person("traditional_401k_contributions", period)
        return where(desired > 0, desired, legacy_desired)
