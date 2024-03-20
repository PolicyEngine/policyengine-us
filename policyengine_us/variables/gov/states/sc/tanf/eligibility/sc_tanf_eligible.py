from policyengine_us.model_api import *


class sc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SC TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("sc_tanf_income_eligible", period)
        resources_eligible = spm_unit("sc_tanf_resources_eligible", period)
        return demographic_eligible & income_eligible & resources_eligible
