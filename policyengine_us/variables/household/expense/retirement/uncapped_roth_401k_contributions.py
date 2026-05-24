from policyengine_us.model_api import *


class uncapped_roth_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped Roth 401(k) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        reported = person("roth_401k_contributions_reported", period)
        legacy_reported = person("roth_401k_contributions", period)
        return where(reported > 0, reported, legacy_reported)
