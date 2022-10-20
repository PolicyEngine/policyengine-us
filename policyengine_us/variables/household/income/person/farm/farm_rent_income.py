from policyengine_us.model_api import *


class farm_rent_income(Variable):
    value_type = float
    entity = Person
    label = "Farm rent net income"
    unit = USD
    definition_period = YEAR
