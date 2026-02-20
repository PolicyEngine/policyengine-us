from policyengine_us.model_api import *


class mt_tanf_net_income_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) net income standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/TANF/TANFStatePlan.pdf#page=10"
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        benefit_standard = spm_unit("mt_tanf_benefit_standard", period)
        p = parameters(period).gov.states.mt.dhs.tanf.income_standards
        return benefit_standard / p.benefit_to_net_factor
