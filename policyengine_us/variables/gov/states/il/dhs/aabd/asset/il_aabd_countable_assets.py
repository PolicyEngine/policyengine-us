from policyengine_us.model_api import *


class il_aabd_countable_assets(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) countable assets"
    )
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.140",
    )
    defined_for = StateCode.IL

    adds = "gov.states.il.dhs.aabd.asset.sources"
