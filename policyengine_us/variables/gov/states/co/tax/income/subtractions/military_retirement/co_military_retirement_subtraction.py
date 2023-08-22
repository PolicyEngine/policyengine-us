from policyengine_us.model_api import *


class co_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado military retirement subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = [
        "co_military_retirement_subtraction_head",
        "co_military_retirement_subtraction_spouse",
    ]
