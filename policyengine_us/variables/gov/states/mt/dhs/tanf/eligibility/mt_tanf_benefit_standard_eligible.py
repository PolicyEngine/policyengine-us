from policyengine_us.model_api import *


class mt_tanf_benefit_standard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Passes Montana TANF Benefit Standard Eligibility Test"
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF604-1Jan012018.pdf#page=2"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        return spm_unit("mt_tanf_countable_income", period) <= spm_unit(
            "mt_tanf_benefit_standard", period
        )
