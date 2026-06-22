from policyengine_us.model_api import *


class nm_ccap_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP based on assets"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    def formula(spm_unit, period, parameters):
        # 8.15.2.11.C(4): family assets may not exceed $1,000,000. New Mexico's
        # limit differs from the federal CCDF default, so we use a state
        # parameter rather than reusing is_ccdf_asset_eligible.
        p = parameters(period).gov.states.nm.ececd.ccap.eligibility
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.asset_limit
