from policyengine_us.model_api import *


class was_tea_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was an Arkansas Transitional Employment Assistance recipient"
    definition_period = YEAR
    defined_for = StateCode.AR
    default_value = False
    reference = (
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=16",
    )
