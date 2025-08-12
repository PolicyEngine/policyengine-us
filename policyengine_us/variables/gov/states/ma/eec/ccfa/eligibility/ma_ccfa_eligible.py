from policyengine_us.model_api import *


class ma_ccfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "EEC Financial Assistance Policy Guide Chapters 3-9"

    def formula(spm_unit, period, parameters):
        # Check all eligibility criteria
        has_eligible_child = (
            add(spm_unit, period, ["ma_ccfa_eligible_child"]) > 0
        )
        income_eligible = spm_unit("ma_ccfa_income_eligible", period)
        asset_eligible = spm_unit("ma_ccfa_asset_eligible", period)
        activity_eligible = spm_unit("ma_ccfa_activity_eligible", period)

        # Special programs that bypass some requirements
        is_dta_related = spm_unit("ma_ccfa_dta_related_eligible", period)
        is_dcf_related = spm_unit("ma_ccfa_dcf_related_eligible", period)
        is_homeless = spm_unit.household("is_homeless", period)

        # Standard eligibility or special program eligibility
        standard_eligible = (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
        )

        special_eligible = is_dta_related | is_dcf_related | is_homeless

        return standard_eligible | special_eligible
