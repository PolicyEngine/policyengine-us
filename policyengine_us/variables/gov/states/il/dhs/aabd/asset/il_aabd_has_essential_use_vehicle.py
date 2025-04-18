from policyengine_us.model_api import *


class il_aabd_has_essential_use_vehicle(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the household has essential use vehicle under the Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.141",
    )
    defined_for = StateCode.IL
