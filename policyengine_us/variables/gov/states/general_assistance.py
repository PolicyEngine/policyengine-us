from policyengine_us.model_api import *


class general_assistance(Variable):
    value_type = float
    entity = Person
    label = "general assistance"
    documentation = (
        "Reported general assistance income. For SNAP, enter only amounts "
        "separate from the state and county cash grants the model already counts."
    )
    unit = USD
    definition_period = YEAR
