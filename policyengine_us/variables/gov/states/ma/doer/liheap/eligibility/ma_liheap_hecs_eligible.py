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
        heating_expense_last_year = spm_unit(
            "heating_expense_last_year", period
        )

        p = parameters(period).gov.states.ma.doer.liheap.hecs.eligibility
        threshold = p.prior_year_cost_threshold[heating_type]

        return heating_expense_last_year > threshold
