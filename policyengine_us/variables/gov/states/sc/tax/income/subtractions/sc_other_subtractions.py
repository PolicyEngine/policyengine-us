from policyengine_us.model_api import *


class sc_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    documentation = (
        "South Carolina other subtractions from income reported on "
        "Form SC1040, Line v (Other subtractions), entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=14"
