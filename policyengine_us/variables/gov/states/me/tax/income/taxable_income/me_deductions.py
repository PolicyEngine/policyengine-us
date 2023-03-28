from policyengine_us.model_api import *


class me_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine income deductions"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.ME
