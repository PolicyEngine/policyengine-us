from policyengine_us.model_api import *


class dc_ccsp_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Child Care Subsidy Program (CCSP) asset"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12"
    defined_for = StateCode.DC

    adds = "gov.states.dc.dhs.ccsp.assets.sources"
