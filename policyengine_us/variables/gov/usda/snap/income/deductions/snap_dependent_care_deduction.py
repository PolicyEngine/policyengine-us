from policyengine_us.model_api import *


class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = USD
    documentation = "Deduction from SNAP gross income for dependent care"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_3"

    adds = ["childcare_expenses"]
