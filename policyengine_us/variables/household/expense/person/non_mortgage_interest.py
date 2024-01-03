from policyengine_us.model_api import *


class non_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Non-mortgage interest"
    unit = USD
    definition_period = YEAR

    adds = ["personal_interest_expense", "investment_interest_expense"]
