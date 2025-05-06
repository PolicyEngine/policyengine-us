from policyengine_us.model_api import *


class ma_liheap_hecs_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = "ma_liheap_hecs_eligible"
    label = "Massachusetts LIHEAP High Energy Cost Supplement (HECS) payout"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)

        return where(
            is_subsidized,
            p.payout.hecs_subsidized[benefit_level],
            p.payout.hecs_non_subsidized[benefit_level],
        )
