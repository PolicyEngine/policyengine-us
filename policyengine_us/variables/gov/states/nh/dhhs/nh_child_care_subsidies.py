from policyengine_us.model_api import *


class nh_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/title-He/subtitle-He-C/chapter-He-C-6900/part-He-C-6910"
    adds = ["nh_ccap"]
