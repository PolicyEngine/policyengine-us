from policyengine_us.model_api import *


class snap_countable_earner(Variable):
    value_type = bool
    entity = Person
    label = "Countable income earner"
    documentation = "Whether this person's earned income is counted for SNAP"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014"

    def formula(person, period, parameters):
        return ~person("snap_excluded_child_earner", period)
