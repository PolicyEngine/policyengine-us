from policyengine_us.model_api import *


class ok_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://oklahoma.gov/okdhs/library/policy/current/oac-340/chapter-10/subchapter-3/parts-3/earned-income-disregard.html"
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf.income

        # Step 1: Get gross earned income from OK-specific TANF variable
        gross_earned = add(spm_unit, period, ["ok_tanf_gross_earned_income"])

        # Step 2: Apply work expense deduction
        # Per OAC 340:10-3-33: $120 for applicants, $240 for recipients with
        # child < 6 working 20+ hours. For simplified implementation, use $120.
        # NOTE: Applicant vs. recipient status cannot be tracked
        work_expense = p.work_expense.applicant
        after_work_expense = max_(gross_earned - work_expense, 0)

        # Step 3: Apply 50% earned income disregard to remainder
        disregard_rate = p.earned_income_disregard_rate
        disregard_amount = after_work_expense * disregard_rate

        return max_(after_work_expense - disregard_amount, 0)
