from policyengine_us.model_api import *


class snap_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = (
        "Earned income deduction for calculating SNAP benefit amount"
    )
    label = "SNAP earned income deduction"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_2"

    def formula(spm_unit, period, parameters):
        deduction_rate = parameters(
            period
        ).gov.usda.snap.income.deductions.earned_income
        # Only apply deduction to earned income from eligible members
        # Per 273.11(c)(1), no earned income deduction for work requirement failures
        eligible_earned_income = spm_unit("snap_earned_income", period)
        return eligible_earned_income * deduction_rate
