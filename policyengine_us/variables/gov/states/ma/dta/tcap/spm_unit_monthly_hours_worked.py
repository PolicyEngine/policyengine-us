from policyengine_us.model_api import *


class spm_unit_monthly_hours_worked(Variable):
    value_type = float
    entity = SPMUnit
    label = "average monthly hours worked"
    unit = "hour"
    documentation = "Hours worked per month on average."
    definition_period = MONTH

    adds = ["monthly_hours_worked"]
