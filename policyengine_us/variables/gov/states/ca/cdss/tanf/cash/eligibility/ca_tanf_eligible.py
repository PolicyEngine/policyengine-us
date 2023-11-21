from policyengine_us.model_api import *


class ca_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        recipient_eligbile = spm_unit("ca_tanf_recipient_eligbile", period)
        resources_eligible = spm_unit("ca_tanf_resources_eligible", period)

        return demographic_eligible & recipient_eligbile & resources_eligible
