from policyengine_us.model_api import *


class sc_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    documentation = (
        "South Carolina other additions to federal taxable income reported on "
        "Form SC1040, Line 2 (Other additions to income), entered as a positive amount, "
        "excluding additions PolicyEngine calculates separately."
    )
    reference = "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=5"
