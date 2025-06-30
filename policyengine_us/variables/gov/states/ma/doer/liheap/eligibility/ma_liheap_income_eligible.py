from policyengine_us.model_api import *


class ma_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts LIHEAP due to income"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ma_liheap_income", period)
        income_threshold = spm_unit(
            "ma_liheap_state_median_income_threshold", period
        )
        return income <= income_threshold
