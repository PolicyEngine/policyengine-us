from policyengine_us.model_api import *


class snap_if_takes_up(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = (
        "SNAP allotment the SPM unit would receive if it takes up the "
        "program, regardless of reported take-up."
    )
    label = "SNAP allotment if takes up"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD
    exhaustive_parameter_dependencies = [
        "gov.usda.snap",
        "gov.ssa",
    ]

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.usda.snap.abolish_snap:
            return 0
        return add(
            spm_unit,
            period,
            [
                "snap_normal_allotment",
                "snap_emergency_allotment",
                "dc_snap_temporary_local_benefit",
            ],
        )
