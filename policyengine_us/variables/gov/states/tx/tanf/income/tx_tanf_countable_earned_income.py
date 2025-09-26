from policyengine_us.model_api import *


class tx_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("tx_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.tx.tanf.income

        # Step 1: Apply work expense deduction
        work_expense_deduction = min_(p.work_expense_deduction, gross_earned)
        earned_after_work_expense = max_(
            gross_earned - work_expense_deduction, 0
        )

        # Step 2: Apply 90% earnings disregard (capped at $1,400)
        # Note: Full implementation would track the 4-month limit in 12-month period
        disregard_rate = p.earned_income_disregard_rate
        disregard_cap = p.earned_income_disregard_cap

        potential_disregard = earned_after_work_expense * disregard_rate
        actual_disregard = min_(potential_disregard, disregard_cap)

        earned_after_disregard = max_(
            earned_after_work_expense - actual_disregard, 0
        )

        # Step 3: For applicants, apply 1/3 disregard
        # Simplified: assuming all are applicants for now
        # Full implementation would track applicant status
        is_applicant = True  # Simplified
        applicant_fraction = p.applicant_earned_income_fraction

        final_countable = where(
            is_applicant & (gross_earned > 0),
            earned_after_disregard * (1 - applicant_fraction),
            earned_after_disregard,
        )

        return final_countable
