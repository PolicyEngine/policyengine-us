from policyengine_us.model_api import *


class snap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for child support payments"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    # Excluding deduction for child support, which applies to the gross income
    # calculation
    adds = ["snap_child_support_deduction_person"]
