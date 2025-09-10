from policyengine_us.model_api import *


class snap_countable_earner(Variable):
    value_type = bool
    entity = Person
    label = "Countable income earner"
    documentation = "Whether this person's earned income is counted for SNAP"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014"

    def formula(person, period, parameters):
        excluded_child = person("snap_excluded_child_earner", period)
        work_req_disqualified = person("snap_work_requirement_disqualified", period)
        # Per 273.11(c)(1), work requirement failures get NO earned income deduction
        # Excluded children also don't get the deduction per standard SNAP rules
        return ~excluded_child & ~work_req_disqualified
