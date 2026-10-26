from policyengine_us.model_api import *


class ut_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    documentation = (
        "Utah other additions to income reported on Form TC-40, Line 5 / "
        "Schedule TC-40A, Part 1, entered as a positive amount."
    )
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html"
