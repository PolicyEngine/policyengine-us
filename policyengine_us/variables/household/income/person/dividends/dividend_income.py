from policyengine_us.model_api import *


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "ordinary dividend income"
    documentation = "Qualified and non-qualified dividends"
    unit = USD
    definition_period = YEAR
    adds = [
        "qualified_dividend_income",
        "non_qualified_dividend_income",
    ]
