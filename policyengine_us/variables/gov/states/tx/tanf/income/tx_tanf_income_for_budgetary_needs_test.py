from policyengine_us.model_api import *


class tx_tanf_income_for_budgetary_needs_test(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF income for budgetary needs test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-408",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Budgetary needs test uses income WITHOUT earned income disregards (1/3 or 90%)
        # Deductions applied:
        # 1. Work expense ($120)
        # 2. Dependent care costs
        # 3. Child support deduction (from unearned income)

        person = spm_unit.members
        p = parameters(period).gov.states.tx.tanf.income

        # Earned income after work expense only (no 1/3 or 90% disregard)
        gross_earned = person("tx_tanf_gross_earned_income", period)
        work_expense = min_(p.deductions.work_expense, gross_earned)
        earned_after_work_expense = max_(gross_earned - work_expense, 0)

        # Sum across household members
        total_earned_after_work_expense = spm_unit.sum(
            earned_after_work_expense
        )

        # Apply dependent care deduction
        dependent_care_deduction = spm_unit(
            "tx_tanf_dependent_care_deduction", period
        )
        earned_after_deductions = max_(
            total_earned_after_work_expense - dependent_care_deduction, 0
        )

        # Add unearned income (already has child support deduction applied)
        unearned_income = spm_unit("tx_tanf_countable_unearned_income", period)

        return earned_after_deductions + unearned_income
