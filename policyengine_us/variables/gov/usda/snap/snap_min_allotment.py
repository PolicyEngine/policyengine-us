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
        p_min = snap.min_allotment
        # Calculate the relevant maximum benefit, defined as the maximum
        # benefit for a household of a certain size in their state.
        snap_region = spm_unit.household("snap_region_str", period)
        relevant_max_allotment = snap.max_allotment.main[snap_region][
            str(p_min.relevant_max_allotment_household_size)
        ]
        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("spm_unit_size", period)
        eligible = size <= p_min.maximum_household_size
        min_allotment = eligible * p_min.rate * relevant_max_allotment
        if p_min.dc.in_effect:
            dc_min_allotment = p_min.dc.amount

            state_code = spm_unit.household("state_code_str", period)
            in_dc = state_code == "DC"
            min_allotment = where(in_dc, dc_min_allotment, min_allotment)

        return min_allotment
