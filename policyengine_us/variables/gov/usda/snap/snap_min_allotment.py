from policyengine_us.model_api import *


class snap_min_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP minimum allotment"
    documentation = (
        "Minimum allotment for SNAP based on household size and state"
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        # Parameters for the minimum benefit.
        snap = parameters(period).gov.usda.snap
        min_allotment = snap.min_allotment
        # Calculate the relevant maximum benefit, defined as the maximum
        # benefit for a household of a certain size in their state.
        snap_region = spm_unit.household("snap_region_str", period)
        relevant_max_allotment = snap.max_allotment.main[snap_region][
            str(min_allotment.relevant_max_allotment_household_size)
        ]
        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("spm_unit_size", period)
        eligible = size <= min_allotment.maximum_household_size
        min_allotment_outside_of_DC = eligible * min_allotment.rate * relevant_max_allotment

        dc_min_alotment = spm_unit("dc_min_allotment", period)

        state_code = spm_unit.household("state_code", period)
        in_dc = state_code == "DC"
        
        return where(in_dc, dc_min, others_min)
