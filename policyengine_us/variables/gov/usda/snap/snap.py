from policyengine_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.usda.snap.abolish_snap:
            return 0
        elif parameters(period).gov.simulation.reported_snap:
            return spm_unit("snap_reported", period) / MONTHS_IN_YEAR
        else:
            return add(
                spm_unit,
                period,
                ["snap_normal_allotment", "snap_emergency_allotment"],
            )
