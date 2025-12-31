from policyengine_us.model_api import *


class de_tanf_countable_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF countable net income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008"
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008 calculation order:
        # 1. Gross earned income
        # 2. Subtract $90 work expense per earner
        # 3. Subtract dependent care expenses
        # NOTE: $30+1/3 and $30 disregards are time-limited and cannot be tracked

        # Step 1: Gross income components
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        gross_unearned = spm_unit("tanf_gross_unearned_income", period)

        # Step 2: Earned income deductions
        work_expense = spm_unit("de_tanf_earned_income_deduction", period)
        dependent_care = spm_unit("de_tanf_dependent_care_deduction", period)
        net_earned = max_(gross_earned - work_expense - dependent_care, 0)

        # Step 3: Unearned income disregard
        child_support_disregard = spm_unit(
            "de_tanf_child_support_disregard", period
        )
        net_unearned = max_(gross_unearned - child_support_disregard, 0)

        return net_earned + net_unearned
