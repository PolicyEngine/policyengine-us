from policyengine_us.model_api import *


class tn_ff_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
