from policyengine_us.model_api import *


class snap_self_employment_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Self-employment income deduction for calculating SNAP benefit amount"
    )
    label = "SNAP self-employment expense deduction"
    unit = USD
    reference = "https://www.snapscreener.com/blog/self-employment"

    adds = ["snap_self_employment_expense_deduction_person"]
