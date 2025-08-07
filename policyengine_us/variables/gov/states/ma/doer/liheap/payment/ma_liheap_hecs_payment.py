from policyengine_us.model_api import *


class ma_liheap_hecs_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP High Energy Cost Supplement (HECS) payment"
    definition_period = YEAR
    defined_for = "ma_liheap_hecs_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap.hecs.amount
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)

        return where(
            is_subsidized,
            p.subsidized[benefit_level],
            p.non_subsidized[benefit_level],
        )
