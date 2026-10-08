from policyengine_us.model_api import *


class non_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Non-mortgage interest paid before the investment interest limit"
    documentation = """
    Non-mortgage interest expenses paid before the 26 U.S.C. 163(d) limit.
    The investment interest component is limited to net investment income
    through Form 4952 when calculating interest_deduction.
    """
    unit = USD
    definition_period = YEAR

    adds = ["investment_interest_expense"]
