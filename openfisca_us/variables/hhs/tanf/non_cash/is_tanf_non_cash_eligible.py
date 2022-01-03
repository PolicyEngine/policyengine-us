from openfisca_us.model_api import *


class is_tanf_non_cash_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligibility for TANF non-cash benefit"
    documentation = "Eligibility for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        assets = spm_unit("snap_assets", period)
        state = spm_unit.household("state_code_str", period)
        limits = parameters(period).hhs.tanf.non_cash
        asset_limit = limits.asset_limit[state]
        income_limit_fpg = limits.gross_income_limit_fpg[state]
        return assets <= asset_limit
