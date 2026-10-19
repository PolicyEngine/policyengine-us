from policyengine_us.model_api import *


class de_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Delaware other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    documentation = (
        "Delaware subtractions from federal adjusted gross income reported on "
        "Form PIT-RES, line 7 (fiduciary adjustments, work opportunity credit, etc.), "
        "entered as a positive amount."
    )
    # PDF pages 6-7
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=6"
