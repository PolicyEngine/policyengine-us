from policyengine_us.model_api import *


class illicit_income(Variable):
    value_type = float
    entity = Person
    label = "Income from bribes, corrupt gifts or other illegal activities."
    unit = USD
    definition_period = YEAR
