from policyengine_us.model_api import *


class spm_unit_weekly_hours_worked(Variable):
    value_type = int
    entity = SPMUnit
    label = "Total amount of weekly hours worked in SPM unit"
    definition_period = YEAR

    adds = ["weekly_hours_worked"]
