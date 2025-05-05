from policyengine_us.model_api import *


class ma_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts LIHEAP due to income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap"

    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        income = add(spm_unit, period, ["irs_gross_income"])
        income_threshold = spm_unit("ma_liheap_state_median_income_threshold", period)
        return income <= income_threshold
