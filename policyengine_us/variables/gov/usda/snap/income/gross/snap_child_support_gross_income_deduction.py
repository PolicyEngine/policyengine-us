from policyengine_us.model_api import *


class snap_child_support_gross_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction from gross income"
    unit = USD
    documentation = (
        "Deduction for child support payments when computing SNAP gross income"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    adds = ["snap_child_support_gross_income_deduction_person"]
