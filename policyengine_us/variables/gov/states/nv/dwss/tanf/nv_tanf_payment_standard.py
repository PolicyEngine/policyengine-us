from policyengine_us.model_api import *


class nv_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.tanf.payment_standard
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_unit_size)
        return p.amount[capped_size]
