from policyengine_us.model_api import *


class mt_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/TANF/TANFStatePlan.pdf#page=10"
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.income_standards
        fpg = spm_unit("mt_tanf_assistance_unit_fpg", period)
        return fpg * p.payment_fpg_rate
