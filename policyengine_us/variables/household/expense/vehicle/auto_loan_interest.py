from policyengine_us.model_api import *


class auto_loan_interest(Variable):
    value_type = float
    entity = Household
    label = "Auto loan interest expense"
    unit = USD
    definition_period = YEAR
