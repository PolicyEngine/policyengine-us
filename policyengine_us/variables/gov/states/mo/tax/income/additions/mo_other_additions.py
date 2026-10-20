from policyengine_us.model_api import *


class mo_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Missouri other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO
    documentation = (
        "Missouri other additions to federal adjusted gross income reported on "
        "Form MO-A, Part 1, Line 6 (Other additions), entered as a positive amount."
    )
    reference = "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=12"
