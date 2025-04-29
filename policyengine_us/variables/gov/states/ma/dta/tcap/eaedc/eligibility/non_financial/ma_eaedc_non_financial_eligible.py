from policyengine_us.model_api import *


class ma_eaedc_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Non-financial eligible for Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010"
    )

    def formula(spm_unit, period, parameters):
        elderly_present = spm_unit("ma_eaedc_eligible_elderly_present", period)
        disabled_head_or_spouse_present = spm_unit(
            "ma_eaedc_eligible_disabled_head_or_spouse", period
        )
        disabled_dependent_present = spm_unit(
            "ma_eaedc_eligible_disabled_dependent_present", period
        )
        caretaker_family_eligible = spm_unit(
            "ma_eaedc_eligible_caretaker_family", period
        )
        immigration_status_eligible = spm_unit(
            "ma_eaedc_immigration_status_eligible", period
        )

        return (
            elderly_present
            | disabled_head_or_spouse_present
            | disabled_dependent_present
            | caretaker_family_eligible
        ) & immigration_status_eligible
