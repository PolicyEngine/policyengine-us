from policyengine_us.model_api import *


class il_aabd_asset_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Illinois Aid to the Aged, Blind or Disabled (AABD) due to asset"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.142",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.asset.disregard
        size = spm_unit("spm_unit_size", period)
        countable_asset = spm_unit("il_aabd_countable_assets", period)
        capped_size = min_(size, 2)
        reduced_unit_size = max_(size - 2, 0)
        p1 = p.base[capped_size]
        pn = p.additional
        asset_disregard = p1 + pn * reduced_unit_size

        return countable_asset <= asset_disregard
