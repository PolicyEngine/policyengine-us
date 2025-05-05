from policyengine_us.model_api import *


class ma_liheap_hecs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.MA
    label = (
        "Eligible for Massachusetts LIHEAP High Energy Cost Supplement (HECS)"
    )
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-and-benefit-chart-january-2025/download"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("ma_liheap_utility_type", period)
        last_year_cost = spm_unit("ma_liheap_last_year_energy_cost", period)

        p = parameters(period).gov.states.ma.doer.liheap.threshold
        threshold = p.hecs_thresholds[utility_type]

        return last_year_cost > threshold
