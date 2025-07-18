from policyengine_us.model_api import *


class dc_ccsp_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to income"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.assets
        asset = spm_unit("dc_ccsp_assets", period)
        return asset <= p.limit
