from policyengine_us.model_api import *


class oasdi_modeled_balance(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "OASDI modeled balance"
    documentation = (
        "Modeled OASDI liabilities (oasdi_income) less modeled benefits "
        "(oasdi_cost). A modeled balance of liabilities and benefits, not a "
        "trust-fund cash balance: it omits reserve interest, Railroad "
        "Retirement interchange, administrative expenses and general-fund "
        "reimbursements."
    )
    unit = USD
    adds = ["oasdi_income"]
    subtracts = ["oasdi_cost"]
