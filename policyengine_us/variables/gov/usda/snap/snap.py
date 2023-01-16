from policyengine_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD
    adds = ["snap_normal_allotment", "snap_emergency_allotment"]
