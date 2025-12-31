from policyengine_us.model_api import *


class nd_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for North Dakota TANF"
    definition_period = MONTH
    reference = "https://www.hhs.nd.gov/applyforhelp/tanf/temporary-assistance-needy-families-program-faqs"
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (age thresholds match federal)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("nd_tanf_income_eligible", period)
        resource_eligible = spm_unit("nd_tanf_resource_eligible", period)
        return demographic_eligible & income_eligible & resource_eligible
