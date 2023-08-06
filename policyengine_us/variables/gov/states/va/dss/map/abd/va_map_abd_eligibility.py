from policyengine_us.model_api import *


class va_map_abd_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        demo_eligible = spm_unit("va_map_abd_demographic_eligibility", period)
        income_eligible = spm_unit("va_map_abd_income_eligibility", period)
        resources_eligible = spm_unit(
            "va_map_abd_resources_eligibility", period
        )
        return demo_eligible & income_eligible & resources_eligible
