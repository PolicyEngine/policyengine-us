from policyengine_us.model_api import *


class tx_ccs_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS asset eligible"
    definition_period = MONTH
    reference = "http://txrules.elaws.us/rule/title40_chapter809_sec.809.41"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs
        assets = spm_unit("spm_unit_assets", period.this_year)
        asset_limit = p.assets.limit
        return assets <= asset_limit
