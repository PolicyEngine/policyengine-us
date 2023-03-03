from policyengine_us.model_api import *


class co_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Colorado TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        # Assume federal demographic eligibility given consistency.
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("co_tanf_income_eligible", period)
        return demographic_eligible & income_eligible
