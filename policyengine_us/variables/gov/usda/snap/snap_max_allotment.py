from policyengine_us.model_api import *


class snap_max_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Maximum SNAP allotment for SPM unit, based on the state group and household size."
    label = "SNAP maximum allotment"
    unit = USD

    def formula(spm_unit, period, parameters):
        max_allotments = parameters(period).gov.usda.snap.max_allotment
        MAX_HOUSEHOLD_SIZE_UNDER_MAIN = 8
        snap_region = spm_unit.household("snap_region_str", period)
        household_size = min_(
            spm_unit("snap_unit_size", period), MAX_HOUSEHOLD_SIZE_UNDER_MAIN
        )
        additional_members = max_(
            0,
            spm_unit("snap_unit_size", period) - MAX_HOUSEHOLD_SIZE_UNDER_MAIN,
        )
        main_allotment = max_allotments.main[snap_region][household_size]
        additional_allotment = (
            additional_members * max_allotments.additional[snap_region]
        )
        return main_allotment + additional_allotment
