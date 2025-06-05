from policyengine_us.model_api import *


class il_aabd(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    adds = ["il_aabd_person"]
