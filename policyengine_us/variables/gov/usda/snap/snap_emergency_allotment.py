from policyengine_us.model_api import *


class snap_emergency_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SNAP emergency allotment"
    label = "SNAP emergency allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period, parameters):
        snap_ea = 0
        for month in period.get_subperiods("month"):
            snap_ea = snap_ea + spm_unit(
                "snap_emergency_allotment_monthly", month
            )
        return snap_ea
