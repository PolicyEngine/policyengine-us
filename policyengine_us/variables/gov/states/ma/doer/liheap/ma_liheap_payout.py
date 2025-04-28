from policyengine_us.model_api import *


class ma_liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    label = "Massachusetts LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("ma_liheap_utility_type", period)
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit(
            "ma_liheap_subsidized_housing_eligible", period
        )

        p = parameters(period).gov.states.ma.doer.liheap

        payout = where(
            is_subsidized,
            p.payout.subsidized[benefit_level][utility_type],
            p.payout.non_subsidized[benefit_level][utility_type],
        )

        return payout
