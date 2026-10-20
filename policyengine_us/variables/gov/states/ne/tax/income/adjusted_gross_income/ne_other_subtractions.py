from policyengine_us.model_api import *


class ne_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE
    documentation = (
        "Nebraska other adjustments decreasing federal adjusted gross income "
        "reported on Form 1040N, Schedule I, Part B, entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=26"
