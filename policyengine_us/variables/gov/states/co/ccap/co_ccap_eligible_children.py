from policyengine_us.model_api import *


class co_ccap_eligible_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of children eligible for Colorado Child Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.CO
    adds = ["co_ccap_child_eligible"]
