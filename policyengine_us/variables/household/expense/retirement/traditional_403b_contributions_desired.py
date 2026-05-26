from policyengine_us.model_api import *


class traditional_403b_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired traditional 403(b) contributions"
    unit = USD
    documentation = (
        "Traditional 403(b) contributions before statutory contribution limits."
    )
    definition_period = YEAR
