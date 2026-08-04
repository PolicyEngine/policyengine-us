from policyengine_us.model_api import *


class ak_ccap_copay_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP family copay rate as share of income"
    definition_period = MONTH
    unit = "/1"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/okdlx2xm/alaska-fics.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.copay
        countable = spm_unit("ak_ccap_countable_income", period)
        monthly_smi = spm_unit("hhs_smi", period)
        smi_ratio = where(monthly_smi > 0, countable / monthly_smi, 0)
        return p.sliding_scale.calc(smi_ratio)
