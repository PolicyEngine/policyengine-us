from policyengine_us.model_api import *


class or_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
    documentation = (
        "Oregon other subtractions from federal taxable income reported on Form "
        "OR-40, Line 13 / Schedule OR-ASC, Section B, entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=14"
