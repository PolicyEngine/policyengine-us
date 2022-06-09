from openfisca_us.model_api import *


class meets_snap_asset_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP asset test"
    unit = USD
    documentation = "Whether the SPM unit's financial resources are within SNAP's allowable limit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        has_elderly_or_disabled = spm_unit("has_usda_elderly_disabled", period)
        asset_test = parameters(period).usda.snap.asset_test
        assets = spm_unit("snap_assets", period)
        asset_limit = where(
            has_elderly_or_disabled,
            asset_test.limit.elderly_disabled,
            asset_test.limit.standard,
        )
        return assets <= asset_limit
