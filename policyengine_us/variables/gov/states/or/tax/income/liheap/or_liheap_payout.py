from policyengine_us.model_api import *


class or_liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = "LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("utility_type", period)
        unit_size = clip(spm_unit("spm_unit_size", period), 1, 6)
        income_range = spm_unit("or_liheap_income_range", period)
        is_region1 = spm_unit("or_liheap_in_region_one", period)
        electricity_type = spm_unit("or_liheap_electricity_type", period)

        p = parameters(period).gov.states["or"].liheap

        # Applies multiplier to the payout when electricity is used for both heating and cooling (not an official policy parameter).
        electricity_multiplier = where(
            (utility_type == utility_type.possible_values.ELECTRICITY)
            & (electricity_type == electricity_type.possible_values.BOTH),
            2,
            1,
        )

        payout = where(
            is_region1,
            p.payout.region_one[unit_size][income_range][utility_type],
            p.payout.region_two[unit_size][income_range][utility_type],
        )

        return payout * electricity_multiplier
