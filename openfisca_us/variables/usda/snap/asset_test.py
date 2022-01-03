from openfisca_us.model_api import *


class snap_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP assets"
    unit = USD
    documentation = "Financial resources used to decide SNAP eligibility"
    definition_period = YEAR


class meets_snap_asset_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP asset test"
    unit = USD
    documentation = "Whether the SPM unit's financial resources are within the allowable limit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        has_elderly_or_disabled = spm_unit("has_elderly_disabled", period)
        asset_test = parameters(period).usda.snap.asset_test
        assets = spm_unit("snap_assets", period)
        asset_limit = where(
            has_elderly_or_disabled,
            asset_test.limit.elderly_disabled,
            asset_test.limit.standard,
        )
        return assets <= asset_limit
