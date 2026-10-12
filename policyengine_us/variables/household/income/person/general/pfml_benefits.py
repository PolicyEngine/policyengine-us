from policyengine_us.model_api import *


# Note that right now this variable is only used for MA CCFA.
class pfml_benefits(Variable):
    value_type = float
    entity = Person
    label = "Paid family and medical leave benefits received"
    unit = USD
    documentation = (
        "Benefits received from a state paid family and medical leave program."
    )
    definition_period = YEAR
