from policyengine_us.model_api import *


class ia_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Iowa other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    documentation = (
        "Iowa other additions to Iowa gross income reported on "
        "Form IA 1040, Line 14 (Other Income), entered as a positive amount."
    )
    reference = "https://revenue.iowa.gov/media/2721/download?inline#page=11"
