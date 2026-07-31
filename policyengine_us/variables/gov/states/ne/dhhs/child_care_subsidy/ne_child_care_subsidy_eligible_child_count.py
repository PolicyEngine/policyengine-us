from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_child_count(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy eligible child count"
    defined_for = StateCode.NE
    adds = ["ne_child_care_subsidy_eligible_child"]
