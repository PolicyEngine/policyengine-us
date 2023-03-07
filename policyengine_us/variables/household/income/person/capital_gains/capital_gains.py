from policyengine_us.model_api import *


class capital_gains(Variable):
    value_type = float
    entity = Person
    label = "capital gains"
    unit = USD
    documentation = "Net gain from disposition of property."
    definition_period = YEAR
    adds = [
        "short_term_capital_gains",
        "long_term_capital_gains",
    ]
