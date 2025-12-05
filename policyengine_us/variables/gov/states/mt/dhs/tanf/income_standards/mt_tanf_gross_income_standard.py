from policyengine_us.model_api import *


class mt_tanf_gross_income_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) gross income standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/TANF/TANFStatePlan.pdf#page=10"
    )

    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.income_standards

        net_income_standard = spm_unit("mt_tanf_net_income_standard", period)
        return net_income_standard * p.net_to_gross_rate
