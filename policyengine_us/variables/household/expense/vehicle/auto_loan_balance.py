from policyengine_us.model_api import *


class auto_loan_balance(Variable):
    value_type = float
    entity = Household
    label = "auto loan total balance"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
