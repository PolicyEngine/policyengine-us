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
        p = parameters(period).gov.usda.snap
        # Calculate the relevant maximum benefit, defined as the maximum
        # benefit for a household of a certain size in their state.
        snap_region = spm_unit.household("snap_region_str", period)
        relevant_max_allotment = p.max_allotment.main[snap_region][
            str(p.min_allotment.relevant_max_allotment_household_size)
        ]
        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("spm_unit_size", period)
        eligible = size <= p.min_allotment.maximum_household_size
        min_allotment = (
            eligible * p.min_allotment.rate * relevant_max_allotment
        )
        p_dc = parameters(period).gov.states.dc.dhs.snap.min_allotment
        if p_dc.in_effect:
            dc_min_allotment = p_dc.amount

            state_code = spm_unit.household("state_code_str", period)
            in_dc = state_code == "DC"
            min_allotment = where(in_dc, dc_min_allotment, min_allotment)

        return min_allotment
