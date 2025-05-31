from policyengine_us.model_api import *


class ma_liheap_state_median_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP state median income threshold"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        state_median_income = spm_unit("hhs_smi", period)
        return state_median_income * p.smi_limit
