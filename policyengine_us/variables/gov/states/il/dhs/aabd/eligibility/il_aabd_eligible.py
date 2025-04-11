from policyengine_us.model_api import *


class il_aabd_eligible_(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-C" #? 
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        asset_eligible = spm_unit("il_aabd_asset_eligible", period)
        ssi_standard_eligible = add(spm_unit, period["is_ssi_eligible_individual"])
        return asset_eligible & ssi_standard_eligible
        