from policyengine_us.model_api import *


class deductible_interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Interest expenses paid before the investment interest limit"
    documentation = """
    Mortgage and non-mortgage interest expenses before the 26 U.S.C. 163(d)
    investment interest limit. interest_deduction replaces investment
    interest paid with the amount allowed on Form 4952 line 8.
    """
    unit = USD
    definition_period = YEAR

    adds = ["deductible_mortgage_interest", "non_mortgage_interest"]
