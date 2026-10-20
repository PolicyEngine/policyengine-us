from policyengine_us.model_api import *


class wv_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    documentation = (
        "West Virginia other additions to federal adjusted gross income reported on "
        "Schedule M, entered as a positive amount, excluding additions PolicyEngine calculates separately."
    )
    reference = "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=5"
