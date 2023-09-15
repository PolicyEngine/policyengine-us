from policyengine_us.model_api import *


class ca_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Resources Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        resources = spm_unit("ca_tanf_resources", period)
        limit = spm_unit("ca_tanf_resouces_limit", period)
        return resources <= limit
