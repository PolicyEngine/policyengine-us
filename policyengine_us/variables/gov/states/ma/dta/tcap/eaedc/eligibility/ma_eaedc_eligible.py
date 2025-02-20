from policyengine_us.model_api import *


class ma_eaedc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        assets_eligible = spm_unit("ma_eaedc_assets_limit_eligible", period)
        income_eligible = spm_unit("ma_eaedc_income_eligible", period)
        age_eligible = spm_unit("ma_eaedc_age_eligible", period)

        disabled_income_eligible = spm_unit(
            "ma_eaedc_disabled_income_eligible", period
        )

        return (
            assets_eligible
            & income_eligible
            & age_eligible
            & disabled_income_eligible
        )
