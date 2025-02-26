from policyengine_us.model_api import *


class or_liheap_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income threshold for Oregon LIHEAP eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        state_median_income = spm_unit("hhs_smi", period)
        p = parameters(period).gov.states["or"].liheap
        return state_median_income * p.state_median_income_rate
