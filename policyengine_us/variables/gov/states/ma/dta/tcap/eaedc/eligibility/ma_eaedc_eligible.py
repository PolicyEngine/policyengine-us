from policyengine_us.model_api import *


class ma_eaedc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010"
    )

    def formula(spm_unit, period, parameters):
        financial_eligible = spm_unit("ma_eaedc_financial_eligible", period)
        non_financial_eligible = spm_unit(
            "ma_eaedc_non_financial_eligible", period
        )
        return financial_eligible & non_financial_eligible
