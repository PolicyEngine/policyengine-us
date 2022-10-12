from policyengine_us.model_api import *


class meets_tanf_non_cash_asset_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets asset test for TANF non-cash benefit"
    documentation = "Asset eligibility for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        assets = spm_unit("snap_assets", period)
        state = spm_unit.household("state_code_str", period)
        limits = parameters(period).gov.hhs.tanf.non_cash
        asset_limit = limits.asset_limit[state]
        return assets <= asset_limit
