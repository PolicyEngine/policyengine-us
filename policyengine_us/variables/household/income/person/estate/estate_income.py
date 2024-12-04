from policyengine_us.model_api import *


class estate_income(Variable):
    value_type = float
    entity = Person
    label = "estate income"
    unit = USD
    definition_period = YEAR
