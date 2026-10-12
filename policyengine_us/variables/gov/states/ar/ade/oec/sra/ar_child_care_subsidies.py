from policyengine_us.model_api import *


class ar_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR
    adds = ["ar_sra"]
