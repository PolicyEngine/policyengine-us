from policyengine_us.model_api import *


class ma_tafdc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010",
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-000",
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        non_financial_eligible = spm_unit(
            "ma_tafdc_non_financial_eligible", period
        )
        financial_eligible = spm_unit("ma_tafdc_financial_eligible", period)

        return non_financial_eligible & financial_eligible
