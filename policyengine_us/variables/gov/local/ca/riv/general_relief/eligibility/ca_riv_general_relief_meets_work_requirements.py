from policyengine_us.model_api import *


class ca_riv_general_relief_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"
    # p.40