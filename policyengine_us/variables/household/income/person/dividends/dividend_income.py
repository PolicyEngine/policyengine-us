from policyengine_us.model_api import *


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "dividend income (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for ordinary_dividend_income. "
        "Use ordinary_dividend_income for new logic."
    )
    unit = USD
    definition_period = YEAR
    adds = ["ordinary_dividend_income"]
