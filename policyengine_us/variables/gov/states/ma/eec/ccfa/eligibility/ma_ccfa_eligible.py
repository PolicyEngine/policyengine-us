from policyengine_us.model_api import *


class ma_ccfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-procedures-manual-february-1-2022/download"

    def formula(spm_unit, period, parameters):
        # Check all eligibility criteria
        has_eligible_child = (
            add(spm_unit, period, ["ma_ccfa_eligible_child"]) > 0
        )

        # TAFDC recipients have categorical eligibility Section 10.05(3)(a)&(b)
        # https://regulations.justia.com/states/massachusetts/606-cmr/title-606-cmr-10-00/section-10-05/
        tafdc_eligible = spm_unit("ma_tafdc_eligible", period)

        # Regular eligibility criteria
        income_eligible = spm_unit("ma_ccfa_income_eligible", period)
        asset_eligible = spm_unit("ma_ccfa_asset_eligible", period)
        activity_eligible = spm_unit("ma_ccfa_activity_eligible", period)

        regular_eligible = (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
        )

        return regular_eligible | tafdc_eligible
