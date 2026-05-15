from policyengine_us.model_api import *


class ak_ccap_dependents_in_care(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of Alaska CCAP-eligible children in care"
    definition_period = MONTH
    defined_for = StateCode.AK
    adds = ["ak_ccap_child_eligible"]
