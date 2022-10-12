from policyengine_us.model_api import *


class capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Capital gains"
    unit = USD
    documentation = "Net gain from disposition of property."
    definition_period = YEAR

    formula = sum_of_variables(
        ["short_term_capital_gains", "long_term_capital_gains"]
    )
