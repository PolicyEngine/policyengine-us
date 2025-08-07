from policyengine_us.model_api import *


class ma_liheap_standard_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP standard payment"
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap.standard.amount
        utility_category = spm_unit("ma_liheap_utility_category", period)
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)

        return where(
            is_subsidized,
            p.subsidized[benefit_level][utility_category],
            p.non_subsidized[benefit_level][utility_category],
        )
