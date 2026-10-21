from policyengine_us.model_api import *


class al_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
    documentation = (
        "Alabama other subtractions from Alabama gross income reported on "
        "Form 40, Page 2, Part II, Line 11 (Other adjustments), entered as a positive amount, "
        "excluding items PolicyEngine calculates separately."
    )
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=14"
    )
