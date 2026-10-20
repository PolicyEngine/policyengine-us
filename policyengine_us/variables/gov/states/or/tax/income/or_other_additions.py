from policyengine_us.model_api import *


class or_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
    documentation = (
        "Oregon other additions to federal taxable income reported on Form "
        "OR-40, Line 8 / Schedule OR-ASC, Section A, entered as a positive amount."
    )
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=14"
