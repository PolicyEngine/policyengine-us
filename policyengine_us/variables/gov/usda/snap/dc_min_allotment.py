from policyengine_us.model_api import *


class dc_min_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "DC SNAP minimum allotment"
    label = "Minimum allotment for SNAP in DC"
    unit = USD
    defined_for = StateCode.DC

    adds = "gov.usda.snap.min_allotment.dc.amount"
