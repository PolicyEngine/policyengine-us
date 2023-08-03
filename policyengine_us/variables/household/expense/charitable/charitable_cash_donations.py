from policyengine_us.model_api import *


class charitable_cash_donations(Variable):
    value_type = float
    entity = Person
    label = "Charitable donations (cash)"
    unit = USD
    definition_period = YEAR
