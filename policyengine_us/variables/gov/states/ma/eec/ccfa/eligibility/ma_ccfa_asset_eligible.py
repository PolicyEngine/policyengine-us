from policyengine_us.model_api import *


class ma_ccfa_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Asset eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=36"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.assets
        total_assets = spm_unit("spm_unit_assets", period.this_year)
        return total_assets < p.limit
