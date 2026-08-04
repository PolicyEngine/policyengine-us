from policyengine_us.model_api import *


class fl_sr_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in the Florida School Readiness program"
    defined_for = StateCode.FL
