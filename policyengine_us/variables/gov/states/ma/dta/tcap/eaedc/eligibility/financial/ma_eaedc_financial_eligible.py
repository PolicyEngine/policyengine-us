from policyengine_us.model_api import *


class ma_eaedc_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Financial eligible for Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-704.000"

    def formula(spm_unit, period, parameters):
        assets_eligible = spm_unit("ma_eaedc_assets_limit_eligible", period)
        income_eligible = spm_unit("ma_eaedc_income_eligible", period)

        return assets_eligible & income_eligible
