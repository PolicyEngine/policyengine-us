from openfisca_us.model_api import *


class snap_net_income_pre_shelter(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SNAP net income before the shelter deduction, needed as intermediate to calculate shelter deduction"
    label = "SNAP net income (pre-shelter)"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_6_A"

    def formula(spm_unit, period):
        income = spm_unit("snap_gross_income", period)
        DEDUCTIONS = [
            "snap_standard_deduction",
            "snap_earned_income_deduction",
        ]
        deductions = add(spm_unit, period, DEDUCTIONS)
        return max_(income - deductions, 0)
