from policyengine_us.model_api import *


class housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance"
    unit = USD
    documentation = "Housing assistance"
    definition_period = YEAR
    defined_for = "is_eligible_for_housing_assistance"
    adds = ["hud_hap"]
