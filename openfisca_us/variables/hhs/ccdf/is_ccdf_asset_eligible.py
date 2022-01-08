from openfisca_us.model_api import *


class is_ccdf_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Asset eligibility for CCDF"

    def formula(spm_unit, period, parameters):
        assets = spm_unit("spm_unit_assets", period)
        p_asset_limit = parameters(period).hhs.ccdf.asset_limit
        return assets <= p_asset_limit
