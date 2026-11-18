from policyengine_us.model_api import *


class wv_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    documentation = (
        "West Virginia other subtractions from federal adjusted gross income reported on "
        "Schedule M, entered as a positive amount, excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=5"
