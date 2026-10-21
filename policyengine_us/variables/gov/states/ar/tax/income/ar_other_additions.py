from policyengine_us.model_api import *


class ar_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Arkansas other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR
    documentation = (
        "Arkansas other additions to gross income reported on Form AR1000F, "
        "Line 22 (Other Income), entered as a positive amount."
    )
    reference = "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
