from policyengine_us.model_api import *


class il_aabd_water_allowance(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) water allowance"
    )
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.payment.utility
        size = spm_unit("spm_unit_size", period)
        area = spm_unit.household("il_aabd_area", period)
        return p.water[area][size]
