from policyengine_us.model_api import *


class non_qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Non-qualified dividend income"
    unit = USD
    definition_period = YEAR
