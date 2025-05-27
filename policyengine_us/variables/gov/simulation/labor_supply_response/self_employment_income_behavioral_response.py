from policyengine_us.model_api import *


class self_employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "self-employment income behavioral response"
    unit = USD
    definition_period = YEAR
    adds = ["labor_supply_behavioral_response"]
    subtracts = ["employment_income_behavioral_response"]
