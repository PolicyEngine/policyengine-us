from policyengine_us.model_api import *


class ut_tanf_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah TANF earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah earned income deductions per R986-200-239:
        # 1. Work expense allowance: $100 per employed person
        # 2. 50% earned income disregard on remaining earned income
        p = parameters(period).gov.states.ut.dwf.tanf.income.deductions

        # Get gross earned income from household members
        person = spm_unit.members
        person_earned = person("tanf_gross_earned_income", period)
        gross_earned = spm_unit.sum(person_earned)

        # Step 1: Work expense deduction ($100 per employed person)
        has_earned_income = person_earned > 0
        employed_count = spm_unit.sum(has_earned_income)
        work_expense_deduction = (
            employed_count * p.work_expense_allowance.amount
        )

        # Step 2: 50% disregard on remainder after work expense
        remainder = max_(gross_earned - work_expense_deduction, 0)
        disregard = remainder * p.earned_income_disregard.rate

        # Total deduction is work expense + 50% disregard
        # But cannot exceed gross earned income
        total_deduction = work_expense_deduction + disregard
        return min_(total_deduction, gross_earned)
