from policyengine_us.model_api import *


class liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = "LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        # Get necessary attributes from the SPM unit
        utility_type = spm_unit("utility_type", period)
        unit_size = spm_unit("spm_unit_size", period)
        income_range = spm_unit("or_liheap_income_range", period)

        # Clip unit size to the valid range (1 to 6)
        unit_size = clip(unit_size, 1, 6)

        # Access LIHEAP payout parameters
        p = parameters(period).gov.states["or"].liheap

        # Determine region using the or_liheap_in_region_one variable
        is_region1 = spm_unit("or_liheap_in_region_one", period)

        # Return the payout based on the region
        return where(
            is_region1,
            p.payout.region_one[unit_size][income_range][utility_type],
            p.payout.region_two[unit_size][income_range][utility_type],
        )
