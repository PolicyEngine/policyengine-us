from policyengine_us.model_api import *

class liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = "LIHEAP Payout"

    def formula(spm_unit, period, parameters):

        utility_type = spm_unit("utility_type", period)
        unit_size = spm_unit("spm_unit_size", period)
        income_range = spm_unit("or_liheap_income_range", period)

        unit_size = clip(unit_size, 1, 6)

        p = parameters(period).gov.states["or"].liheap

        is_region1 = spm_unit("or_liheap_in_region_one", period)

        return where(
            is_region1,
            p.payout.region_one[unit_size][income_range][utility_type],
            p.payout.region_two[unit_size][income_range][utility_type]
        )
