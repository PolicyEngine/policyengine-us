from policyengine_us.model_api import *


class snap_net_income_pre_shelter(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "SNAP net income before the shelter deduction, needed as intermediate to calculate shelter deduction"
    label = "SNAP net income (pre-shelter)"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_6_A"

    def formula(spm_unit, period, parameters):
        """
        A household shall be entitled, with respect to expenses other than
        expenses paid on behalf of the household by a third party, to an excess
        shelter expense deduction to the extent that the monthly amount
        expended by a household for shelter exceeds an amount equal to 50
        percent of monthly household income after all other applicable
        deductions have been allowed.
        """
        income = spm_unit("snap_gross_income", period)
        all_deductions = parameters(
            period
        ).gov.usda.snap.income.deductions.allowed
        deductions_except_shelter = [
            deduction
            for deduction in all_deductions
            if deduction != "snap_excess_shelter_expense_deduction"
        ]
        deduction_value = add(spm_unit, period, deductions_except_shelter)
        return max_(income - deduction_value, 0)
