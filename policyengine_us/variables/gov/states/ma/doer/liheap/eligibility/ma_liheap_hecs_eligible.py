from policyengine_us.model_api import *


class ma_liheap_hecs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Massachusetts LIHEAP High Energy Cost Supplement (HECS)"
    )
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("ma_liheap_heating_type", period)
        last_year_energy_cost = spm_unit(
            "ma_liheap_last_year_energy_cost", period
        )

        p = parameters(period).gov.states.ma.doer.liheap.threshold
        threshold = p.hecs_thresholds[heating_type]

        return last_year_energy_cost > threshold
