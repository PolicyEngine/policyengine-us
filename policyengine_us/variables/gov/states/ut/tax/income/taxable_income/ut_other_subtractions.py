from policyengine_us.model_api import *


class ut_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    documentation = (
        "Utah other subtractions from income reported on Form TC-40, Line 8 / "
        "Schedule TC-40A, Part 2, entered as a positive amount, excluding subtractions "
        "PolicyEngine calculates separately."
    )
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html"
