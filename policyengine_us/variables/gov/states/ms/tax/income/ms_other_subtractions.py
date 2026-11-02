from policyengine_us.model_api import *


class ms_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Mississippi other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    documentation = (
        "Mississippi other adjustments to gross income for deductions reported on Form 80-105 "
        "that PolicyEngine does not compute: moving expense (Line 54), catastrophe savings (Line 60), "
        "first-time home buyer (Line 62), agricultural disaster (Line 63) and ABLE (Line 64) "
        "deductions, plus adjustments entered as negative amounts on Schedule N, "
        "entered as a positive amount."
    )
    # PDF pages 12-13, 16
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12"
