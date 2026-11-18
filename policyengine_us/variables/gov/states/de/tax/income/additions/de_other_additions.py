from policyengine_us.model_api import *


class de_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Delaware other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    documentation = (
        "Delaware additions to federal adjusted gross income reported on "
        "Form PIT-RES, line 3 (fiduciary adjustments, oil depletion, etc.), "
        "entered as a positive amount."
    )
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=5"
