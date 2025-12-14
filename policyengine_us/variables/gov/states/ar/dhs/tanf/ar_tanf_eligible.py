from policyengine_us.model_api import *


class ar_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TANF eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ar_tanf_income_eligible", period)
        resources_eligible = spm_unit("ar_tanf_resources_eligible", period)
        # Use federal demographic eligibility (already SPM unit-level)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        return income_eligible & resources_eligible & demographic_eligible
