from policyengine_us.model_api import *


class snap_normal_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = (
        "Normal SNAP benefit amount, equal to net income minus food contribution"
    )
    label = "SNAP normal allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD
    defined_for = "is_snap_eligible"

    adds = ["snap_allotment_before_eligibility"]
