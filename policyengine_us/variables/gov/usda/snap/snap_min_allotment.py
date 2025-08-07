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
            str(snap.min_allotment.relevant_max_allotment_household_size)
        ]

        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("snap_unit_size", period)
        eligible = size <= snap.min_allotment.maximum_household_size
        min_allotment = eligible * min_allotment.rate * relevant_max_allotment

        # DC, NM, MD and NJ provide separate minimum allotment amounts
        state_code = spm_unit.household("state_code_str", period)

        p_dc = parameters(period).gov.states.dc.dhs.snap.min_allotment
        if p_dc.in_effect:
            dc_min_allotment = p_dc.amount
            in_dc = state_code == "DC"
            min_allotment = where(in_dc, dc_min_allotment, min_allotment)

        p_md = parameters(period).gov.states.md.usda.snap.min_allotment
        if p_md.in_effect:
            md_min_allotment = p_md.amount
            in_md = state_code == "MD"
            has_elderly = spm_unit("md_snap_elderly_present", period)
            min_allotment = where(
                in_md & has_elderly, md_min_allotment, min_allotment
            )

        p_nj = parameters(period).gov.states.nj.snap
        if p_nj.in_effect:
            nj_min_allotment = p_nj.amount
            in_nj = state_code == "NJ"
            min_allotment = where(in_nj, nj_min_allotment, min_allotment)

        return min_allotment
