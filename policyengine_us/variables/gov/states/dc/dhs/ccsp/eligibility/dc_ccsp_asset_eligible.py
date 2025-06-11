from policyengine_us.model_api import *


class dc_ccsp_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to income"
    definition_period = MONTH
    reference = ""
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.asset
        return asset < 1,000,000
