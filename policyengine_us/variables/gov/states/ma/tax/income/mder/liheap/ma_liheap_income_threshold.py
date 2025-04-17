from policyengine_us.model_api import *


class ma_liheap_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income threshold for Massachusetts LIHEAP eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap"

    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        state_median_income = spm_unit("hhs_smi", period)
        p = parameters(period).gov.hhs.liheap
        return state_median_income * p.income_rate
