from policyengine_us.model_api import *


class me_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine deduction"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.ME
