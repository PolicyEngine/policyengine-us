from policyengine_us.model_api import *


class ia_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("ia_tanf_income_eligible", period)
        return demographic_eligible & income_eligible
