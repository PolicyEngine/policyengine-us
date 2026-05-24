from policyengine_us.model_api import *


class uncapped_roth_403b_contributions(Variable):
    value_type = float
    entity = Person
    label = "Uncapped Roth 403(b) contributions"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        reported = person("roth_403b_contributions_reported", period)
        legacy_reported = person("roth_403b_contributions", period)
        return where(reported > 0, reported, legacy_reported)
