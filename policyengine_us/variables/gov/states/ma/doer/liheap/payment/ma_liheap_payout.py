from policyengine_us.model_api import *


class ma_liheap_payout(Variable):
    value_category = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    label = "Massachusetts LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap
        utility_category = spm_unit("ma_liheap_utility_category", period)
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)
        hecs_payout = spm_unit("ma_liheap_hecs_payout", period)

        standard_payout = where(
            is_subsidized,
            p.standard_payout.subsidized[benefit_level][utility_category],
            p.standard_payout.non_subsidized[benefit_level][utility_category],
        )

        return standard_payout + hecs_payout
