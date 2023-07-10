from policyengine_us.model_api import *


class vt_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Vermont standard deduction, including bonus for aged or blind."
    )
    reference = "Hold"
    defined_for = StateCode.VT
