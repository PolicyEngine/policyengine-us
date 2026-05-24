from policyengine_us.model_api import *


class traditional_401k_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired traditional 401(k) contributions"
    unit = USD
    documentation = (
        "Traditional 401(k) contributions before statutory contribution limits."
    )
    definition_period = YEAR
