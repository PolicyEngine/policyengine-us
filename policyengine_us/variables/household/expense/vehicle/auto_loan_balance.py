from policyengine_us.model_api import *


class auto_loan_balance(Variable):
    value_type = float
    entity = Household
    label = "Auto loan total balance"
    unit = USD
    definition_period = YEAR
