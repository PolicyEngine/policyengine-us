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
        relevant_max_allotment = p.max_allotment.main[snap_region][
            str(p.min_allotment.relevant_max_allotment_household_size)
        ]

        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("spm_unit_size", period)
        eligible = size <= min_allotment.maximum_household_size
        base_benefit_amount = (
            eligible * min_allotment.rate * relevant_max_allotment
        )

        # New Jersey provides a separate minimum allotment amount after 2023
        if snap.temporary_local_benefit.nj.in_effect:
             state_code = spm_unit.household("state_code_str", period)
             in_nj = state_code == "NJ"
             nj_min_allotment = snap.temporary_local_benefit.nj.amount
             base_benefit_amount = where(in_nj, nj_min_allotment, base_benefit_amount)
        return base_benefit_amount
