from policyengine_us.model_api import *


class sc_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina retirement deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    adds = [
        "sc_retirement_deduction_indv",  # p1,p2
        "sc_retirement_deduction_survivors",  # p3
    ]
