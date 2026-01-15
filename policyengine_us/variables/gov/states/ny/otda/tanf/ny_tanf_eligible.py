from policyengine_us.model_api import *


class ny_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF eligible"
    definition_period = MONTH
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("ny_tanf_income_eligible", period)
        asset_eligible = spm_unit("ny_tanf_resources_eligible", period)
        return demographic_eligible & income_eligible & asset_eligible
