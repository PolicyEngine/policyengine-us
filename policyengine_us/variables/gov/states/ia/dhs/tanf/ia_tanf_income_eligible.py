from policyengine_us.model_api import *


class ia_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        gross_income_eligible = spm_unit(
            "ia_tanf_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("ia_tanf_net_income_eligible", period)
        payment_standard_eligible = spm_unit(
            "ia_tanf_payment_standard_eligible", period
        )
        return (
            gross_income_eligible
            & net_income_eligible
            & payment_standard_eligible
        )
