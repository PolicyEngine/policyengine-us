from policyengine_us.model_api import *


class ga_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1605/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/1615/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        # PAMMS 1605 Step 8: "Allow all applicable earned income deductions
        # to the gross countable earned income of each employed individual
        # to determine the net earned income"
        # PAMMS 1615: "Deductions are applied in the order listed:
        # 1. $250 standard work expense, 2. Dependent care"

        # Sum person-level earned income after work expense disregard
        earned_after_disregard = add(
            spm_unit, period, ["ga_tanf_earned_income_after_disregard"]
        )

        # Apply childcare deduction to earned income only
        childcare_deduction = spm_unit("ga_tanf_childcare_deduction", period)
        net_earned = max_(earned_after_disregard - childcare_deduction, 0)

        # PAMMS 1605 Step 9: "Add the unearned income of all individuals
        # to the net earned income to determine the net countable income"
        # PAMMS 1605: "Deductions are not allowed to unearned income"
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Net countable income = net earned + unearned
        return net_earned + unearned
