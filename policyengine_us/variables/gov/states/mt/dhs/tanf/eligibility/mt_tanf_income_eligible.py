from policyengine_us.model_api import *


class mt_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Montana Temporary Assistance for Needy Families (TANF) due to income"
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF604-1Jan012018.pdf#page=1"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        gmi_eligible = spm_unit("mt_tanf_gmi_eligible", period)
        benefit_standard_eligible = spm_unit(
            "mt_tanf_benefit_standard_eligible", period
        )
        payment_standard_eligible = spm_unit(
            "mt_tanf_payment_standard_eligible", period
        )

        return (
            gmi_eligible
            & benefit_standard_eligible
            & payment_standard_eligible
        )
