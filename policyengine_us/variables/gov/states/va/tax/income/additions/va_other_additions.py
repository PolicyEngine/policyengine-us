from policyengine_us.model_api import *


class va_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    documentation = (
        "Virginia other additions to federal adjusted gross income reported on "
        "Schedule ADJ, Line 2b (Other additions), entered as a positive amount."
    )
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=24"
