from policyengine_us.model_api import *


class deductible_interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on all loans"
    unit = USD
    definition_period = YEAR

    adds = ["deductible_mortgage_interest", "non_mortgage_interest"]
