from policyengine_us.model_api import *


class ri_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Rhode Island CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.6.1",
        "https://dhs.ri.gov/media/10606/download?language=en",
    )

    def formula(spm_unit, period, parameters):
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        p = parameters(period).gov.states.ri.dhs.ccap.copay
        countable_income = spm_unit("ri_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)
        copay_rate = p.rate.calc(fpl_ratio)
        copay = countable_income * copay_rate
        return where(is_homeless, 0, copay)
