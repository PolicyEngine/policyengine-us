from policyengine_us.model_api import *


class va_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("va_tanf_income_eligibility", period)
        return demographic_eligible & income_eligible