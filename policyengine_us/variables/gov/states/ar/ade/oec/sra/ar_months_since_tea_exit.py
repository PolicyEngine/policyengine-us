from policyengine_us.model_api import *


class ar_months_since_tea_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since Arkansas TEA cash aid ended"
    definition_period = MONTH
    defined_for = StateCode.AR
    default_value = 0
    reference = "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=16"
