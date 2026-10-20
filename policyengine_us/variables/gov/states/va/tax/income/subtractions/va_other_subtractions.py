from policyengine_us.model_api import *


class va_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    documentation = (
        "Virginia other subtractions from federal adjusted gross income reported on "
        "Schedule ADJ, Line 6b (Other subtractions), entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=24"
