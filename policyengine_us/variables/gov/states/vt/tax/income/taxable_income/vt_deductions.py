from policyengine_us.model_api import *


class vt_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income deductions"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.VT
