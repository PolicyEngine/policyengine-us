from policyengine_us.model_api import *


class ss_aime_input(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security AIME (direct input)"
    documentation = (
        "Optional direct input for Average Indexed Monthly Earnings. "
        "When provided, bypasses the 45-year earnings lookback "
        "calculation. Users can find their AIME on their SSA "
        "statement."
    )
    unit = USD
    default_value = 0
