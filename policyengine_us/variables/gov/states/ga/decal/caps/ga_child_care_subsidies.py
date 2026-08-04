from policyengine_us.model_api import *


class ga_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    adds = ["ga_caps"]
