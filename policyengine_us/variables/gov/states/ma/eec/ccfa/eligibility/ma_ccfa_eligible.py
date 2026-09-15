from policyengine_us.model_api import *


class ma_ccfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=10",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=17",
    )

    def formula(spm_unit, period, parameters):
        has_child = add(spm_unit, period, ["ma_ccfa_eligible_child"]) > 0
        # As in other state CCDF models, reported TANF enrollment is the
        # proxy for DTA-related care; agency referral issuance is not modeled.
        tafdc_enrolled = spm_unit("is_tanf_enrolled", period)
        regular = spm_unit("ma_ccfa_income_eligible", period) & spm_unit(
            "ma_ccfa_activity_eligible", period
        )
        return (
            has_child
            & spm_unit("ma_ccfa_asset_eligible", period)
            & (tafdc_enrolled | regular)
        )
