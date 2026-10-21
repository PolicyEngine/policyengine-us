from policyengine_us.model_api import *


class ia_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Iowa other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    documentation = (
        "Iowa other subtractions from Iowa gross income reported on "
        "Form IA 1040, Line 24 (Other Adjustments), entered as a positive amount, "
        "excluding items PolicyEngine calculates separately."
    )
    reference = "https://revenue.iowa.gov/media/2721/download?inline#page=23"
