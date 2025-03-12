from policyengine_us.model_api import *


class ma_eaedc_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Non-financial eligible for Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010"

    def formula(spm_unit, period, parameters):
        elderly_age_eligible = spm_unit("ma_eaedc_elderly_age_eligible", period)
        disabled_eligible = spm_unit("ma_eaedc_disabled_eligible", period)
        disabled_dependent_present_eligible = spm_unit(
            "ma_eaedc_disabled_dependent_present_eligible", period
        )
        caretaker_family_eligible = spm_unit(
            "ma_eaedc_caretaker_family_eligible", period
        )

        return (
            elderly_age_eligible
            | disabled_eligible
            | disabled_dependent_present_eligible
            | caretaker_family_eligible
        )
        