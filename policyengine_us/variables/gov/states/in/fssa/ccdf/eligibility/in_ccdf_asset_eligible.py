from policyengine_us.model_api import *


class in_ccdf_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF asset eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=31"
    )

    def formula(spm_unit, period, parameters):
        # The Manual (Section on assets, page 31) excludes the home and main
        # vehicle; we don't subtract those at the moment, which is negligible
        # against the $1,000,000 threshold.
        p = parameters(period).gov.states["in"].fssa.ccdf.assets
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.limit
