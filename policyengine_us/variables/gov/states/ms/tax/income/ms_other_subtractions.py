from policyengine_us.model_api import *


class ms_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Mississippi other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    documentation = (
        "Mississippi other adjustments to gross income reported on "
        "Form 80-105, Line 66 (Other Adjustments), entered as a positive amount, "
        "excluding items PolicyEngine calculates separately."
    )
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12"
