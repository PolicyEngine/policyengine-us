from policyengine_us.model_api import *


class va_pregnant_women_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA Pregnant Women eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        pregnant_eligible = spm_unit(
            "va_pregnant_women_pregnant_eligibility", period
        )
        income_eligible = spm_unit(
            "va_pregnant_women_income_eligibility", period
        )
        return pregnant_eligible & income_eligible
