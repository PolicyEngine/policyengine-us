from policyengine_us.model_api import *


class al_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
    documentation = (
        "Alabama other additions to Alabama gross income reported on "
        "Form 40, Page 2, Part I, Line 4 (Other income), entered as a positive amount."
    )
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=14"
    )
