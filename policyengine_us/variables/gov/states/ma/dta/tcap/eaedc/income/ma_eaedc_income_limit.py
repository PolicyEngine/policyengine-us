from policyengine_us.model_api import *


class ma_eaedc_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-440"
    )
    
    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
        living_arrangement = spm_unit("ma_eaedc_living_arrangement",period)
        p_income_limit = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        p1 = p_income_limit.base[living_arrangement]
        pn = p_income_limit.increment[living_arrangement]
        return  p1+pn*(n-1)
        