from policyengine_us.model_api import *


class uncapped_roth_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped Roth 401(k) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        desired = person("roth_401k_contributions_desired", period)
        legacy_desired = person("roth_401k_contributions", period)
        return where(desired > 0, desired, legacy_desired)
