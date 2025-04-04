from policyengine_us.model_api import *


class ma_tafdc_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        immigration_eligible = spm_unit(
            "ma_tafdc_immigration_status_eligible", period
        )
        dependent_criteria_eligible = spm_unit(
            "ma_tafdc_dependent_criteria_eligible", period
        )
        eaedc_eligible = spm_unit("ma_eaedc_eligible", period)
        return (
            immigration_eligible
            & dependent_criteria_eligible
            & ~eaedc_eligible
        )
