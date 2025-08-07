from policyengine_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD
    exhaustive_parameter_dependencies = [
        "gov.usda.snap",
        "gov.ssa",
    ]

    def formula(spm_unit, period, parameters):
        takes_up = spm_unit("takes_up_snap_if_eligible", period)
        is_in_microsim = hasattr(spm_unit.simulation, "dataset")
        if parameters(period).gov.usda.snap.abolish_snap:
            return 0
        elif parameters(period).gov.simulation.reported_snap:
            return spm_unit("snap_reported", period)
        else:
            value = add(
                spm_unit,
                period,
                [
                    "snap_normal_allotment",
                    "snap_emergency_allotment",
                    "dc_snap_temporary_local_benefit",
                ],
            )
            if is_in_microsim:
                return value * takes_up
            else:
                return value
