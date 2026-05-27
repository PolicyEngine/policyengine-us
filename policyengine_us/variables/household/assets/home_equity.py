from policyengine_us.model_api import *


class home_equity(Variable):
    value_type = float
    entity = Person
    label = "Home equity"
    documentation = "Equity interest in a primary residence."
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
