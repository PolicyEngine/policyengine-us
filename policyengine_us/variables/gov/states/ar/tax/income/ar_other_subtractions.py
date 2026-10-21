from policyengine_us.model_api import *


class ar_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Arkansas other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR
    documentation = (
        "Arkansas other subtractions from gross income reported on Form AR1000F, "
        "Line 29 (Other Adjustments), entered as a positive amount, excluding items PolicyEngine calculates separately."
    )
    reference = "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=15"
